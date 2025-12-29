import sys
from pathlib import Path
import math

# 运行目录加入sys.path
run_dir = Path(__file__).parent
# 是否存在sys.path
if run_dir not in sys.path:
    sys.path.append(r"C:\\Users\\Administrator\\Desktop\\PlayVideo")
    
from Code.base_window import MainWindow
from PySide6.QtWidgets import QFileDialog, QMessageBox,QAbstractSlider
from pymxs import runtime as rt
from PySide6.QtCore import Qt, QTimer
from PySide6.QtMultimedia import QMediaPlayer
from PySide6.QtMultimediaWidgets import QVideoWidget
from PySide6.QtCore import QUrl
from PySide6.QtGui import QColor, QPalette

class PlayVideo(MainWindow):
    def __init__(self):
        super().__init__()
        self.script_path = Path(__file__).parent
        self.script_name = Path(__file__).stem
        self.last_open_dir = str(Path.home() / "Videos")
        self.load_ui()
        self._player = QMediaPlayer()
        self.videoWidget = QVideoWidget()
        
        # 视频时间与3ds Max帧的同步相关变量
        self.max_fps = rt.frameRate  # 获取3ds Max当前帧率
        self.is_syncing_to_max = False  # 防止循环同步的标志
        self.sync_timer = QTimer()  # 定时器用于定期同步到3ds Max
        self.sync_timer.setInterval(100)  # 每100毫秒同步一次（可调整）
        
        self._init_ui_state()
        
        palette = self.videoWidget.palette()
        # 使用 QColor 设置为灰色 (128, 128, 128)
        palette.setColor(QPalette.Window, QColor(128, 128, 128))
        self.videoWidget.setPalette(palette)
        self.videoWidget.setAutoFillBackground(True)
        self.videoWidget.setAspectRatioMode(Qt.IgnoreAspectRatio)
        self._player.setVideoOutput(self.videoWidget)
        self.ui.hlayout.addWidget(self.videoWidget)
        self.connect()
        self.setup_max_sync()

    def _init_ui_state(self):
        """初始化UI状态"""
        self.ui.time_label.setText("00:00 / 00:00")
        self.ui.slider.setValue(0)
        self.ui.slider.setEnabled(False)  # 初始时禁用滑块

    def connect(self):
        self.ui.selectVideo_Button.clicked.connect(self.select_video)
        self._player.durationChanged.connect(self.update_duration)
        self._player.positionChanged.connect(self.update_position)
        self._player.errorOccurred.connect(self.handle_player_error)
        self._player.mediaStatusChanged.connect(self.handle_media_status)
        self.ui.slider.sliderPressed.connect(self.slider_pressed)
        self.ui.slider.sliderReleased.connect(self.slider_released)
        self.ui.slider.sliderMoved.connect(self.set_video_position)
        self.ui.slider.actionTriggered.connect(self.on_action_triggered)
        self.ui.syncFromMax_CheckBox.stateChanged.connect(self.toggle_sync_from_max)
        self.ui.syncToMax_CheckBox.stateChanged.connect(self.toggle_sync_from_max)
        # 连接同步定时器
        self.sync_timer.timeout.connect(self.sync_to_max)
        
        # 3ds Max相关按钮连接
        if hasattr(self.ui, 'setStartTime_Button'):
            self.ui.setStartTime_Button.clicked.connect(self.set_max_start_time)
        if hasattr(self.ui, 'setEndTime_Button'):
            self.ui.setEndTime_Button.clicked.connect(self.set_max_end_time)
        # if hasattr(self.ui, 'syncToMax_CheckBox'):
        #     self.ui.syncToMax_CheckBox.stateChanged.connect(self.toggle_max_sync)
    
    def toggle_sync_from_max(self, state):
        sender = self.sender()  # 获取发送信号的CheckBox

        # 如果是syncFromMax_CheckBox发送的信号
        if sender == self.ui.syncFromMax_CheckBox:
            self.ui.syncToMax_CheckBox.blockSignals(True)
            self.ui.syncToMax_CheckBox.setChecked(False)
            self.ui.syncToMax_CheckBox.blockSignals(False)

        elif sender == self.ui.syncToMax_CheckBox:
            
            self.ui.syncFromMax_CheckBox.blockSignals(True)
            self.ui.syncFromMax_CheckBox.setChecked(False)
            self.ui.syncFromMax_CheckBox.blockSignals(False)

    def on_action_triggered(self, action):
        """响应各种滑块动作"""
        if action == QAbstractSlider.SliderSingleStepAdd.value:
            position = self.ui.slider.value()+self.ui.slider.singleStep()
            self.slider_released_action(position)
        elif action == QAbstractSlider.SliderSingleStepSub.value:
            position = self.ui.slider.value()-self.ui.slider.singleStep()
            self.slider_released_action(position)
            
        elif action == QAbstractSlider.SliderPageStepAdd.value:
            position = self.ui.slider.value()+self.ui.slider.PageStep()
            self.slider_released_action(position)
            
        elif action == QAbstractSlider.SliderPageStepSub.value:
            position = self.ui.slider.value()-self.ui.slider.PageStep()
            self.slider_released_action(position)

    def slider_released_action(self,position):
        """滑块释放时设置位置并继续播放"""

        self.ui.slider.setValue(position)
        self._player.setPosition(position)
        # 同步到3ds Max
        self._player.pause()
        self.sync_video_to_max(position)

    def setup_max_sync(self):
        """设置3ds Max同步功能"""
        # 监听3ds Max时间滑块变化
        try:
            # 注册回调函数，当3ds Max时间改变时调用
            # rt.callbacks.addScript(rt.Name('timeChanged'), self.on_max_time_changed)
            rt.registerTimeCallback(self.on_max_time_changed) 
        except:
            print("无法注册3ds Max时间变化回调")

    def select_video(self):
        """打开文件对话框选择视频文件"""
        file_name, _ = QFileDialog.getOpenFileName(
            self,
            "选择视频文件",
            self.last_open_dir,
            "视频文件 (*.mp4 *.avi *.mov *.mkv *.wmv *.flv);;所有文件 (*.*)"
        )
        
        if file_name:
            self.last_open_dir = str(Path(file_name).parent)
            self.load_video(file_name)
    
    def load_video(self, file_path):
        """加载视频文件"""
        try:
            self._player.setSource(QUrl.fromLocalFile(file_path))
            self._player.play()
            # self._player.setPosition(1)
            
            # 更新窗口标题显示当前播放的文件
            self.setWindowTitle(f'个人模仿秀 - {Path(file_path).name}')
            
            # 启用滑块
            self.ui.slider.setEnabled(True)
            
            # 自动设置3ds Max的开始和结束时间
            self.auto_set_max_time_range()
            
        except Exception as e:
            QMessageBox.warning(self, "错误", f"无法播放视频:\n{str(e)}")

    def format_time(self, ms):
        """将毫秒转换为 MM:SS 格式"""
        seconds = int(ms / 1000)
        minutes = int(seconds / 60)
        seconds = int(seconds % 60)
        return f"{minutes:02d}:{seconds:02d}"
    
    def format_time_with_frames(self, ms):
        """将毫秒转换为 MM:SS:FF 格式（包含帧）"""
        seconds = ms / 1000.0
        minutes = int(seconds / 60)
        seconds = seconds % 60
        frames = int(seconds * self.max_fps)
        seconds_int = int(seconds)
        frames = int((seconds - seconds_int) * self.max_fps)
        return f"{minutes:02d}:{seconds_int:02d}:{frames:02d}"
    
    def ms_to_frames(self, ms):
        """将毫秒转换为帧数"""
        seconds = ms / 1000.0
        return int(seconds * self.max_fps)
    
    def frames_to_ms(self, frames):
        """将帧数转换为毫秒"""
        seconds = frames / self.max_fps
        return int(seconds * 1000)
    
    def update_duration(self, duration):
        """更新视频总时长"""
        if duration > 0:
            self.total_duration = duration
            self.ui.slider.setMaximum(duration)
            self.ui.slider.setSingleStep(self.max_fps)
            self.ui.slider.setPageStep(self.max_fps)
            self.ui.slider.setTickInterval(self.max_fps)
            self.update_time_label(self._player.position())
            
            # 显示包含帧数的时间
            if hasattr(self.ui, 'frame_label'):
                total_frames = self.ms_to_frames(duration)
                self.ui.frame_label.setText(f"总帧数: {total_frames}")

    def update_time_label(self, position):
        """更新时间显示标签"""
        current_time = self.format_time(position)
        total_time = self.format_time(self.total_duration)
        self.ui.time_label.setText(f"{current_time} / {total_time}")
        
        # 同时显示帧数格式
        if hasattr(self.ui, 'frame_time_label'):
            current_frame_time = self.format_time_with_frames(position)
            total_frame_time = self.format_time_with_frames(self.total_duration)
            self.ui.frame_time_label.setText(f"{current_frame_time} / {total_frame_time}")

    def update_position(self, position):
        """当视频播放位置改变时，更新滑条的位置"""
        # 更新滑块位置（阻止信号防止循环）
        self.ui.slider.blockSignals(True)
        self.ui.slider.setValue(position)
        self.ui.slider.blockSignals(False)
        
        # 更新时间标签
        self.update_time_label(position)
        
        # 同步到3ds Max（如果启用）
        self.sync_to_max()

    def update_slider_range(self, duration):
        """当视频时长改变时，设置滑条的范围"""
        self.ui.slider.setRange(0, duration)

    def slider_pressed(self):
        """滑块被按下时暂停视频"""
        self._player.pause()
    
    def slider_released(self):
        """滑块释放时设置位置并继续播放"""
        position = self.ui.slider.value()

        self._player.setPosition(position)
        # 同步到3ds Max
        self.sync_video_to_max(position)
    


    def set_video_position(self, position):
        """设置视频位置"""
        self._player.setPosition(position)

        self._player.pause()
        # 同步到3ds Max
        self.sync_video_to_max(position)
        
        # 更新时间标签
        self.update_time_label(position)

    def handle_player_error(self, error, error_string):
        """处理播放器错误"""
        if error != QMediaPlayer.NoError:
            QMessageBox.warning(self, "播放错误", f"播放器错误:\n{error_string}")
    
    def handle_media_status(self, status):
        """处理媒体状态变化"""
        if status == QMediaPlayer.EndOfMedia:
            # 视频播放结束时重置
            self._player.setPosition(0)
            # 同步重置3ds Max时间
            self.sync_video_to_max(0)

    # ========== 3ds Max 同步功能 ==========
    
    def toggle_max_sync(self, state):
        """切换3ds Max同步功能"""
        if state == Qt.Checked:
            self.sync_timer.start()
        else:
            self.sync_timer.stop()
    
    def sync_to_max(self):
        """将视频时间同步到3ds Max时间轴"""
        if not hasattr(self, 'total_duration') or self.total_duration == 0:
            return
            
        # 检查是否启用同步
        if hasattr(self.ui, 'syncToMax_CheckBox') and not self.ui.syncToMax_CheckBox.isChecked():
            return
            
        if self.is_syncing_to_max:
            return
            
        self.is_syncing_to_max = True
        
        try:
            # 获取当前视频位置
            video_position = self._player.position()
            
            # 转换为3ds Max帧
            current_frame = self.ms_to_frames(video_position)
            
            # 设置3ds Max当前时间
            rt.sliderTime = current_frame
            
        except Exception as e:
            print(f"同步到3ds Max失败: {e}")
        finally:
            self.is_syncing_to_max = False
    
    def sync_video_to_max(self, position_ms):
        """将指定视频位置同步到3ds Max"""
        if hasattr(self.ui, 'syncToMax_CheckBox') and not self.ui.syncToMax_CheckBox.isChecked():
            return
            
        try:
            current_frame = self.ms_to_frames(position_ms)
            rt.sliderTime = current_frame
        except Exception as e:
            print(f"同步视频位置到3ds Max失败: {e}")
    
    def on_max_time_changed(self):
        """当3ds Max时间改变时的回调函数"""
        # 检查是否启用从3ds Max到视频的同步
        if hasattr(self.ui, 'syncFromMax_CheckBox') and self.ui.syncFromMax_CheckBox.isChecked():
            try:
                current_frame = rt.sliderTime+self.ui.spinBox.value()

                position_ms = self.frames_to_ms(current_frame)
                
                # 确保不超过视频总时长
                if hasattr(self, 'total_duration'):
                    position_ms = min(position_ms, self.total_duration)

                # 设置视频位置
                self._player.setPosition(position_ms)
                self.ui.slider.setValue(position_ms)
                self.update_time_label(position_ms)
                self._player.pause()
            except Exception as e:
                print(f"从3ds Max同步到视频失败: {e}")
    
    def set_max_start_time(self):
        """设置3ds Max动画开始时间为视频当前时间"""
        try:
            current_frame = self.ms_to_frames(self._player.position())
            rt.animationRange = rt.interval(current_frame, rt.animationRange.end)
            QMessageBox.information(self, "成功", f"已设置开始时间为第 {current_frame} 帧")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"设置开始时间失败:\n{str(e)}")
    
    def set_max_end_time(self):
        """设置3ds Max动画结束时间为视频当前时间"""
        try:
            current_frame = self.ms_to_frames(self._player.position())
            rt.animationRange = rt.interval(rt.animationRange.start, current_frame)
            QMessageBox.information(self, "成功", f"已设置结束时间为第 {current_frame} 帧")
        except Exception as e:
            QMessageBox.warning(self, "错误", f"设置结束时间失败:\n{str(e)}")
    
    def auto_set_max_time_range(self):
        """自动设置3ds Max的动画时间范围为视频时长"""
        if not hasattr(self, 'total_duration') or self.total_duration == 0:
            return
            
        try:
            # 等待一下确保视频时长已加载
            from PySide6.QtCore import QTimer
            QTimer.singleShot(500, self._do_auto_set_time_range)
        except:
            pass
    
    def _do_auto_set_time_range(self):
        """执行自动设置时间范围"""
        try:
            total_frames = self.ms_to_frames(self.total_duration)
            rt.animationRange = rt.interval(0, total_frames)
            
            if hasattr(self.ui, 'autoSync_CheckBox') and self.ui.autoSync_CheckBox.isChecked():
                QMessageBox.information(self, "自动设置", 
                                      f"已自动设置3ds Max动画范围:\n"
                                      f"开始: 0 帧\n"
                                      f"结束: {total_frames} 帧\n"
                                      f"时长: {self.format_time(self.total_duration)}")
        except Exception as e:
            print(f"自动设置时间范围失败: {e}")

    def closeEvent(self, event):
        """窗口关闭事件"""
        self._player.stop()
        self.sync_timer.stop()
        
        # 移除3ds Max回调
        try:
            # rt.callbacks.removeScripts(rt.Name('timeChanged'))
            rt.unRegisterTimeCallback(self.on_max_time_changed)
        except:
            pass
            
        super().closeEvent(event)

# 主程序
window = PlayVideo()
# 窗口置顶
window.setWindowFlags(window.windowFlags() | Qt.WindowStaysOnTopHint)
# 窗口标题
window.setWindowTitle('个人模仿秀 - 3ds Max视频同步')
# 窗口大小
window.resize(800, 500)  # 稍微调大窗口以容纳更多控件
window.show()
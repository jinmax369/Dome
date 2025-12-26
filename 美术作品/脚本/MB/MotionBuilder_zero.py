from pyfbsdk import *

lModelList = FBModelList()
FBGetSelectedModels(lModelList)
lScene = FBSystem().Scene

def tPoseAngleMatch(FBVector3d):
    '''
    This function is helping rig to Tpose-ish. Select a joint and execute it.
    '''
    for i, angle in enumerate(FBVector3d):
        negative = False
        if angle < 0:
            angle = abs(angle)
            negative = True
        if 0 <= angle < 45:
            angle = 0
        elif 45 <= angle < 135:
            angle = 90
        elif 135 <= angle < 225:
            angle = 180
        elif 225 <= angle < 315:
            angle = 270
        elif 315 <= angle:
            angle = 360
        if negative == True:
            angle = -angle
        FBVector3d[i] = angle
    return FBVector3d

def getGlobalRotate(lModel):
    globalRotation = FBVector3d()
    lModel.GetVector(globalRotation, FBModelTransformationType.kModelRotation, True)
    print("Current Global Rotation:", globalRotation)
    return globalRotation

if len(lModelList) == 0:
    FBMessageBox("Message", "Nothing selected", "OK", None, None)
else:
    modifiedmodels = []
    for model in lModelList:
        print(model.Name)
        tPoseAngle = tPoseAngleMatch(getGlobalRotate(model))
        model.SetVector(tPoseAngle, FBModelTransformationType.kModelRotation)
        # Refresh the scene after setting transforms
        lScene.Evaluate()
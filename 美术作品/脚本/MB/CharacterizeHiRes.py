from pyfbsdk import *
from pyfbsdk_additions import *

def addJointToCharacter ( characterObject, slot, jointName ):
    
    myJoint = FBFindObjectByFullName('Model::' + jointName)
    property = characterObject.PropertyList.Find(slot + "Link")
    property.append (myJoint)
        
def CharacterizeHiRes(charName):
    
    # make a character
    myCharacter = FBCharacter (charName)
    # Assign the models to the slots
    addJointToCharacter (myCharacter, 'Reference', charName)
    addJointToCharacter (myCharacter, 'Hips', 'Hips')
    addJointToCharacter (myCharacter, 'LeftUpLeg', 'LeftUpLeg')
    addJointToCharacter (myCharacter, 'LeftLeg', 'LeftLeg')
    addJointToCharacter (myCharacter, 'LeftFoot', 'LeftFoot')
    addJointToCharacter (myCharacter, 'RightUpLeg', 'RightUpLeg')
    addJointToCharacter (myCharacter, 'RightLeg', 'RightLeg')
    addJointToCharacter (myCharacter, 'RightFoot', 'RightFoot')
    addJointToCharacter (myCharacter, 'Spine', 'Spine')
    addJointToCharacter (myCharacter, 'LeftArm', 'LeftArm')
    addJointToCharacter (myCharacter, 'LeftForeArm', 'LeftForeArm')
    addJointToCharacter (myCharacter, 'LeftHand', 'LeftHand')
    addJointToCharacter (myCharacter, 'RightArm', 'RightArm')
    addJointToCharacter (myCharacter, 'RightForeArm', 'RightForeArm')
    addJointToCharacter (myCharacter, 'RightHand', 'RightHand')
    addJointToCharacter (myCharacter, 'Head', 'Head')
    addJointToCharacter (myCharacter, 'LeftToeBase', 'LeftToeBase')
    addJointToCharacter (myCharacter, 'RightToeBase', 'RightToeBase')
    addJointToCharacter (myCharacter, 'LeftShoulder', 'LeftShoulder')
    addJointToCharacter (myCharacter, 'RightShoulder', 'RightShoulder')
    addJointToCharacter (myCharacter, 'Spine1', 'Spine1')
    addJointToCharacter (myCharacter, 'Spine2', 'Spine2')
    addJointToCharacter (myCharacter, 'Spine3', 'Spine3')
    addJointToCharacter (myCharacter, 'Neck', 'Neck')
    # turn character on, for some reason this often causes mB2012 to crash.
    myCharacter.SetCharacterizeOn(1) 

#characterize hiRes
CharacterizeHiRes('MyCharacter')
##   ____           _                ____
##  / ___|__ _  ___| |_ _   _ ___   / ___|__ _ _ __  _   _  ___  _ __
## | |   / _` |/ __| __| | | / __| | |   / _` | '_ \| | | |/ _ \| '_ \
## | |__| (_| | (__| |_| |_| \__ \ | |__| (_| | | | | |_| | (_) | | | |
##  \____\__,_|\___|\__|\__,_|___/  \____\__,_|_| |_|\__, |\___/|_| |_|
##                                                   |___/
##           ___ ___  _  _ _____ ___ _  _ _   _ ___ ___
##          / __/ _ \| \| |_   _|_ _| \| | | | | __|   \
##         | (_| (_) | .` | | |  | || .` | |_| | _|| |) |
##          \___\___/|_|\_| |_| |___|_|\_|\___/|___|___/
##
## A P-ROC Project by Eric Priepke, Copyright 2012
## Built on the PyProcGame Framework from Adam Preble and Gerry Stellenberg
## Original Cactus Canyon software by Matt Coriale
##
##
## This mode keeps track of the awards and points for making the left ramp
## The intent is to have this be an always on mode, but to separate the code for readability
##

from procgame import dmd
import ep

class LeftRamp(ep.EP_Mode):
    """Cactus Canyon Left Ramp Mode"""
    def __init__(self, game, priority):
        super(LeftRamp, self).__init__(game, priority)
        self.myID = "Left Ramp"
        # Set up the sounds
        # set up the animations
        self.border = dmd.FrameLayer(opaque=False, frame=self.game.assets.dmd_woodcutBorder.frames[0])

    def mode_started(self):
        self.game.lamp_control.left_ramp()

    def mode_stopped(self):
        self.game.lamp_control.left_ramp('Disable')

    def sw_leftRampEnter_active(self,sw):
        # hitting this switch counts as a made ramp - really
        # tick one onto the total of ramp shots
        self.game.increase_tracking('leftRampShots')
        # check the chain status
        if ep.last_shot == "right":
            # if we're coming from the right ramp, chain goes up
            self.game.combos.increase_chain()
        else:
            # if we're not, reset the chain to one
            self.game.combos.chain = 1
        # score the points and mess with the combo
        if self.game.combos.myTimer > 0:
            # register the combo and reset the timer - returns true for use later
            combo = self.game.combos.hit()
        else:
            # and turn on the combo timer - returns false for use later
            combo = self.game.combos.start()

        # if a polly mode is running, let it go man
        if self.game.peril:
            pass
        else:
            # play the river ramp sound
            self.game.sound.play(self.game.assets.sfx_leftRampEnter)

            self.award_ramp_score(combo)

        ## -- set the last switch hit --
        ep.last_switch = "leftRampEnter"
        ep.last_shot = "left"


    def sw_leftRampMake_active(self,sw):
        # in general gameplay this switch has no purpose
        # but I'm sure it adds points
        self.game.score_with_bonus(2530)
        ## -- set the last switch hit --
        ep.last_switch = "leftRampMake"


    def award_ramp_score(self, combo=False):
        # cancel any other displays
        for mode in self.game.ep_modes:
            if getattr(mode, "abort_display", None):
                mode.abort_display()

        ##
        ##
        # set the animation

        ## ramp award is determined by stage - starts at 1
        ## completed is CURRENTLY 4 - to reset the awards
        ## reset the leftRampStage
        stage = self.game.show_tracking('leftRampStage')
        if stage == 1:
            self.awardString = "WHITE WATER"
            self.awardPoints = str(ep.format_score(125000))
            self.game.score_with_bonus(125000)
            self.game.base.play_quote(self.game.assets.quote_leftRamp1)
            # load the 2 animations
            anim1 = self.game.assets.dmd_blankRiver
            anim2 = self.game.assets.dmd_rowboat
            # set up the layers
            animLayer1 = dmd.AnimatedLayer(frames=anim1.frames,hold=True,opaque=True,repeat=False,frame_time=5)
            animLayer2 = dmd.AnimatedLayer(frames=anim2.frames,hold=True,opaque=False,repeat=False,frame_time=5)
            # layer 2 needs transparent
            animLayer2.composite_op = "blacksrc"
            # math out the wait
            myWait = len(anim1.frames) / 12.0
            # combine the 2 layers
            animLayer = dmd.GroupedLayer(128,32,[animLayer1,animLayer2])
            # turn it on
            self.layer = animLayer
            # set a delay to show the award
            self.delay(name="Display",delay=myWait,handler=self.show_award_text)
        elif stage == 2:
            self.awardString = "WATER FALL"
            self.awardPoints = str(ep.format_score(150000))
            self.game.score_with_bonus(150000)
            self.game.base.play_quote(self.game.assets.quote_leftRamp2)
            # load the animation
            anim = self.game.assets.dmd_riverChase
            # math out the wait
            myWait = len(anim.frames) / 12.0
            # set the animation
            animLayer = dmd.AnimatedLayer(frames=anim.frames,hold=True,opaque=True,repeat=False,frame_time=5)
            # turn it on
            self.layer = animLayer
            # set the delay for the award
            self.delay(name="Display",delay=myWait,handler=self.show_award_text)

        elif stage == 3:
            # if drunk stacking isn't allowed - don't start save polly
            if self.game.drunk_multiball.running and not self.game.base.drunkStacking:
                self.score_with_bonus(50000)
            else:
                # stage 3 now starts river chase
                self.game.increase_tracking('leftRampStage')
                self.game.modes.add(self.game.river_chase)
                self.game.river_chase.start_river_chase()

        else:
            start_value = self.game.increase_tracking('adventureCompleteValue',5000)
            if self.game.river_chase.won:
                self.awardString = "POLLY SAVED"
                self.game.base.play_quote(self.game.assets.quote_victory)
                value = start_value
            else:
                self.awardString = "POLLY KIDNAPPED"
                value = start_value / 10
            self.awardPoints = str(ep.format_score(value))
            self.game.score_with_bonus(value)
            # play animation if we're not in a combo after level 4
            if combo:
                self.layer = None
                self.game.combos.display()
            else:
                self.anim_river_victory()

        # then tick the stage up for next time unless it's completed
        if stage < 3:
            self.game.increase_tracking('leftRampStage')
            # do a little lamp flourish
            self.game.lamps.leftRampWhiteWater.schedule(0x00FF00FF)
            self.game.lamps.leftRampWaterfall.schedule(0x0FF00FF0)
            self.game.lamps.leftRampSavePolly.schedule(0xFF00FF00)
            # update the lamps
            self.delay(delay=1,handler=self.lamp_update)
            print "CHECING TRACKING Left ramp LR: " + str(self.game.show_tracking('leftRampStage'))

    # for now since this doesn't blink there's just one step
    def show_award_text(self,blink=None):
        # create the two text lines
        awardTextTop = dmd.TextLayer(128/2,5,self.game.assets.font_5px_bold_AZ,justify="center",opaque=False)
        awardTextBottom = dmd.TextLayer(128/2,11,self.game.assets.font_15px_az,justify="center",opaque=False)
        # if blink frames we have to set them
        if blink:
            awardTextTop.set_text(self.awardString,blink_frames=12)
            awardTextBottom.set_text(self.awardPoints,blink_frames=12)
        else:
            awardTextTop.set_text(self.awardString)
            awardTextBottom.set_text(self.awardPoints)
        # combine them
        completeFrame = dmd.GroupedLayer(128, 32, [self.border,awardTextTop,awardTextBottom])
        # swap in the new layer
        #self.layer = completeFrame
        transition = ep.EP_Transition(self,self.layer,completeFrame,ep.EP_Transition.TYPE_PUSH,ep.EP_Transition.PARAM_WEST)
        # clear in 2 seconds
        self.delay(name="Display",delay=2,handler=self.clear_layer)
        # show combo display if the chain is high enough
        if self.game.combos.chain > 1:
            self.delay(name="Display",delay=2,handler=self.game.combos.display)

    def anim_river_victory(self):
        if self.game.river_chase.won:
            print "RIVER VICTORY"
            self.game.sound.play(self.game.assets.sfx_grinDing)
            victoryLayer = dmd.FrameLayer(opaque=False, frame=self.game.assets.dmd_pollyVictory.frames[12])
            self.layer = victoryLayer
        else:
            backdrop = dmd.FrameLayer(opaque=True, frame=self.game.assets.dmd_poutySheriff.frames[0])
            textLine1 = dmd.TextLayer(25,8,self.game.assets.font_12px_az,justify="center",opaque=False).set_text("YOU")
            textLine2 = dmd.TextLayer(98,8,self.game.assets.font_12px_az,justify="center",opaque=False).set_text("LOST!")
            combined = dmd.GroupedLayer(128,32,[backdrop,textLine1,textLine2])
            self.game.sound.play(self.game.assets.sfx_glumRiffShort)

            self.layer = combined
        self.delay(name="Display",delay=1,handler=self.show_award_text)

    def push_out(self):
        print "TRANSITION MF"
        blank = dmd.FrameLayer(opaque=False, frame=self.game.assets.dmd_blank.frames[0])
        blank.composite_op = "blacksrc"
        transition = ep.EP_Transition(self,self.layer,blank,ep.EP_Transition.TYPE_PUSH,ep.EP_Transition.PARAM_WEST)
        transition.callback = self.clear_layer

    def abort_display(self):
        self.clear_layer()
        self.cancel_delayed("Display")

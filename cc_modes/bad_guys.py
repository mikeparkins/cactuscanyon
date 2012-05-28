##
##
##
##  Drop Target info:
##  Left to right - 0,1,2,3
##  Switches = badGuySW#
##     Lamps = badGuyL#
##     Coils = badGuyC#

from procgame import *
import cc_modes
import ep
import random
import procgame

class BadGuys(game.Mode):
    """BadGuys for great justice - covers Quickdraw, Showdown, and ... ? """
    def __init__(self,game,priority):
        super(BadGuys, self).__init__(game,priority)
        self.coils = [self.game.coils.badGuyC0,
                      self.game.coils.badGuyC1,
                      self.game.coils.badGuyC2,
                      self.game.coils.badGuyC3]
        self.lights = [self.game.lamps.badGuyL0,
                       self.game.lamps.badGuyL1,
                       self.game.lamps.badGuyL2,
                       self.game.lamps.badGuyL3]
        self.posts = [self.game.coils.leftGunFightPost,
                      self.game.coils.rightGunFightPost]
        #efault
        self.side = 0
        self.showdownValue = 300000

    def ball_drained(self):
    # if we're dropping down to one ball, and showdown is running - do stuff
        if self.game.num_balls_in_play == 1 and "SHOWDOWN" in self.game.show_tracking('quickdrawStatus'):
            self.end_showdown()
        if self.game.trough.num_balls_in_play == 0:
            if "RUNNING" or "SHOWDOWN" in self.game.show_tracking('quickdrawStatus') or self.game.show_tracking('gunfightStatus') == "RUNNING":
                self.dispatch_delayed()
                for coil in self.coils:
                    coil.disable()
                for coil in self.posts:
                    coil.disable()
                if self.game.show_tracking('quickdrawStatus',self.side) == "RUNNING":
                    self.quickdraw_lost(self.side)
                if self.game.show_tracking('quickdrawStatus',self.side) == "SHOWDOWN":
                    self.end_showdown()
                if self.game.show_tracking('gunfightStatus') == "RUNNING":
                    self.gunfight_lost()

    def sw_badGuySW0_active(self,sw):
        # far left bad guy target
        print "BAD GUY 1 HIT"
        if self.game.show_tracking('badGuyUp',0):
            self.hit_bad_guy(0)

    def sw_badGuySW1_active(self,sw):
        # center left badguy target
        print "BAD GUY 2 HIT"
        if self.game.show_tracking('badGuyUp',1):
            self.hit_bad_guy(1)

    def sw_badGuySW2_active(self,sw):
        # center right bad guy target
        print "BAD GUY 3 HIT"
        if self.game.show_tracking('badGuyUp',2):
            self.hit_bad_guy(2)

    def sw_badGuySW3_active(self,sw):
        print "BAD GUY 4 HIT"
        # far right bad guy target
        if self.game.show_tracking('badGuyUp',3):
            self.hit_bad_guy(3)

    def hit_bad_guy(self,target):
        # stop the timer
        # kill the coil to the drop target based on position
        self.target_down(target)
        # call back to base to turn on the light for this bad guy?

        # If there's a quickdraw running
        if "RUNNING" in self.game.show_tracking('quickdrawStatus'):
            # kill the timer
            self.cancel_delayed("Grace")
            self.cancel_delayed("Timer Delay")
            # It's been won
            self.quickdraw_won(target)
        # Otherwise, if all badguys are dead, we're in a showdown
        elif "SHOWDOWN" in self.game.show_tracking('quickdrawStatus'):
            print "SHOWDOWN RUNNING OMG"
            self.showdown_hit(target)
            # showdown stuff would go here
        # option 3 is a gunfight
        else:
            self.gunfight_won()

    ## Trapping the return lane activity during gunfight/quickdraw/showdown
    def sw_leftReturnLane_active(self, sw):
        # register a left return lane hit
        self.return_lane_hit(0)
        return procgame.game.SwitchStop

    def sw_rightReturnLane_active(self,sw):
        # register a right return lane hit
        self.return_lane_hit(1)
        return procgame.game.SwitchStop

    def return_lane_hit(self,side):
        # score some points and play a sound
        self.game.score(2530)
        self.game.sound.play(self.game.assets.sfx_rattlesnake)

    def target_up(self,target):
        self.coils[target].patter(on_time=4,off_time=16,original_on_time=35)
        self.lights[target].enable()
        self.delay(delay=0.1,handler=self.target_activate,param=target)

    def target_down(self,target):
        # kill the delay that enables switch recognition - this is for gunfights mostly
        self.game.set_tracking('badGuyUp',False,target)
        self.coils[target].disable()
        self.lights[target].disable()

    def target_activate(self,target):
        self.game.set_tracking('badGuyUp',True,target)

    def clear_layer(self):
        self.layer = None
    ###
    ###   ___        _      _       _
    ###  / _ \ _   _(_) ___| | ____| |_ __ __ ___      __
    ### | | | | | | | |/ __| |/ / _` | '__/ _` \ \ /\ / /
    ### | |_| | |_| | | (__|   < (_| | | | (_| |\ V  V /
    ###  \__\_\\__,_|_|\___|_|\_\__,_|_|  \__,_| \_/\_/
    ###

    def start_quickdraw(self,side):
        self.side = side
        print "STARTING QUICKDRAW ON SIDE:" + str(side)
        # set the status of this side to running
        self.game.set_tracking('quickdrawStatus',"RUNNING",side)
        # figure out the available bad guys
        choices = []
        count = 0
        for x in self.game.show_tracking('badGuysDead'):
            if not x:
                choices.append(count)
            count += 1

        print "AVAILABLE BAD GUYS"
        print choices
        # pick one of them at random
        target = random.choice(choices)
        print "BAD GUY ACTIVE IS: " + str(target)
        # kill the game music
        print "START QUICKDRAW IS KILLING THE MUSIC"

        self.game.sound.stop_music()
        # start the mode music
        self.game.sound.play(self.game.assets.music_quickdrawBumper)
        self.delay(name="quickdraw music",delay=1.3,handler=self.game.play_remote_music,param=self.game.assets.music_quickdraw)
        # play a quote
        self.game.sound.play_voice(self.game.assets.quote_quickdrawStart)
        # pop that sucker up
        self.target_up(target)
        # Set up the display
        anim = dmd.Animation().load(ep.DMD_PATH+'quickdraw-start.dmd')
        self.animLayer = dmd.AnimatedLayer(frames=anim.frames,hold=True,opaque=False,repeat=False,frame_time=6)
        # set the end time based on the config setting
        # set up the point value
        value = [500000,750000,1000000,1500000,2000000]
        # based on rank
        rank = self.game.show_tracking('rank')
        self.points = value[rank]
        scoreLayer = dmd.TextLayer(84, 4, self.game.assets.font_12px_az, "center", opaque=False).set_text(ep.format_score(self.points))
        # combine the score and animation and turn it on
        self.layer = dmd.GroupedLayer(128,32,[self.animLayer,scoreLayer])
        # read the run time from the settings
        self.runtime = self.game.user_settings['Gameplay (Feature)']['Quickdraw Timer']
        # set the amount to subtract per 5th of a second
        # I hope this is right - divide the points by 10, divide by 5 times the amount of seconds, times 10 again to get an even number
        # then take off 370 to get a more interesting countdown
        self.portion = ((self.points / 10) / int(self.runtime * 5) * 10) - 370
        # queue up a delay for when the timer should run out if the mode hasn't been won
        # then start the timer after a 1 second grace period
        self.delay(name="Grace",delay=1.5,handler=self.quickdraw_timer,param=target)

    def quickdraw_timer(self,target):
        # ok, so this has to control the score and display?
        # for now stepping in 1/5 second
        self.runtime -= 0.2
        if self.runtime <= 0:
            # timer runs out - player lost
            self.quickdraw_lost(target)
        else:
            # every 3 seconds, play a taunt quote
            if int(self.runtime % 3.0) == 0 and self.runtime >= 5:
                self.game.sound.play_voice(self.game.assets.quote_quickdrawTaunt)
            # take points off the score
            self.points -= self.portion
            # update the score text layer
            scoreLayer = dmd.TextLayer(84, 4, self.game.assets.font_12px_az, "center", opaque=False).set_text(ep.format_score(self.points))
            self.layer = dmd.GroupedLayer(128,32,[self.layer,scoreLayer])
            # update the group layer
            # make it active
            self.layer = dmd.GroupedLayer(128,32,[self.animLayer,scoreLayer])
            # delay the next iteration
            self.delay("Timer Delay", delay = 0.2, handler = self.quickdraw_timer, param=target)

    def quickdraw_won(self,target):
        # kill the mode music
        print "QUICKDRAW WON IS KILLING THE MUSIC"

        self.game.sound.stop_music()
        # play the win animation
        anim = dmd.Animation().load(ep.DMD_PATH+'quickdraw-hit.dmd')
        animLayer = dmd.AnimatedLayer(frames=anim.frames,hold=True,opaque=False,repeat=False,frame_time=6)
        #  setup the text
        scoreLayer = dmd.TextLayer(84, 4, self.game.assets.font_12px_az, "center", opaque=False).set_text(ep.format_score(self.points))
        # combine and activate
        textLayer = dmd.TextLayer(84,20, self.game.assets.font_7px_bold_az, "center", opaque=False).set_text("QUICK DRAW!")
        self.game.sound.play(self.game.assets.sfx_quickdrawHit)
        self.game.sound.play(self.game.assets.sfx_quickdrawCheer)
        self.layer = dmd.GroupedLayer(128,32,[animLayer,scoreLayer,textLayer])
        myWait = len(anim.frames) / 10.0 + 1
        # play a quote
        self.game.sound.play(self.game.assets.quote_quickdrawWin)
        # stuff specific to winning
        # score the points
        self.game.score(self.points)
        # update the bad guys
        self.game.set_tracking('badGuysDead',"True",target)
        self.update_lamps()
        # end the quickdraw after the animation bit - and maybe pad for sound
        self.delay(delay=myWait,handler=self.quickdraw_check_bounty)

    def quickdraw_check_bounty(self):
        # if the bounty isn't lit, light bounty - should these stack?
        # TODO stock game does not stack bounties - might be fun to add that
        if not self.game.show_tracking('isBountyLit'):
            # turn off the current layer
            self.layer = None
            # run the light bounty
            self.game.saloon.light_bounty()
            # shutdown wait to cover the bounty display
            self.delay(delay=1.6,handler=self.end_quickdraw)
        else:
            self.end_quickdraw()


    def quickdraw_lost(self,target):
        # kill the mode music
        print "QUICKDRAW LOST IS KILLING THE MUSIC"
        self.game.sound.stop_music()
        # stuff specific to losing
        # drop the coil and kill the lamp
        self.target_down(target)
        # else just end the quickdraw
        self.end_quickdraw()

    def end_quickdraw(self):
        # status passes won/lost?
        print "ENDING QUICKDRAW"
        # set the status to OPEN
        self.game.set_tracking('quickdrawStatus',"OPEN",self.side)
        # turn off the layer
        self.layer = None
        # play a parting quote?
        # If all the bad guys are now dead - SHOWDOWN - TODO may need to move this to win or whatever - investigate process
        if False not in self.game.show_tracking('badGuysDead'):

            self.start_showdown()
        else:
            self.game.update_lamps()
            # turn the main music back on
            self.game.base_game_mode.music_on()
            # unload this piece
            self.game.modes.remove(self.game.bad_guys)

    ###
    ###  ____  _                      _
    ### / ___|| |__   _____      ____| | _____      ___ __
    ### \___ \| '_ \ / _ \ \ /\ / / _` |/ _ \ \ /\ / / '_ \
    ###  ___) | | | | (_) \ V  V / (_| | (_) \ V  V /| | | |
    ### |____/|_| |_|\___/ \_/\_/ \__,_|\___/ \_/\_/ |_| |_|
    ###

    ## Just an experiment at this point
    ## right now, showdown will just end when 8 guys are killed

    def start_showdown(self):
        print "S H O W D O W N"
        # kill the GI
        self.game.base_game_mode.gi_toggle("OFF")
        # things, they go here
        self.deathTally = 0
        # set the tracking
        self.game.set_tracking('quickdrawStatus',"SHOWDOWN",self.side)
        # kick out more ball
        # pop up the targets
        # play a startup animation
        anim = dmd.Animation().load(ep.DMD_PATH+'showdown.dmd')
        myWait = len(anim.frames) / 10.0
        animLayer = ep.EP_AnimatedLayer(anim)
        animLayer.hold=True
        animLayer.frame_time = 6
        # keyframe sounds
        animLayer.add_frame_listener(2,self.game.play_remote_sound,param=self.game.assets.sfx_lightning1)
        animLayer.add_frame_listener(2,self.lightning,param="top")
        animLayer.add_frame_listener(4,self.lightning,param="top")
        animLayer.add_frame_listener(5,self.lightning,param="left")
        animLayer.add_frame_listener(8,self.game.play_remote_sound,param=self.game.assets.sfx_lightningRumble)
        animLayer.add_frame_listener(8,self.lightning,param="top")
        animLayer.add_frame_listener(10,self.lightning,param="top")
        animLayer.add_frame_listener(11,self.lightning,param="left")
        # setup the display
        self.layer = animLayer
        self.delay(delay=myWait,handler=self.get_going)

    def get_going(self):
        self.game.sound.play(self.game.assets.quote_showdown)
        # turn the GI back on
        self.game.base_game_mode.gi_toggle("ON")
        # add a ball
        self.add_ball()
        # start the music
        self.game.sound.play_music(self.game.assets.music_showdown,loops=-1)
        #self.showdown_reset_guys()
        self.new_rack_pan()

    def add_ball(self):
        self.game.autoPlunge = True
        self.game.trough.launch_balls(1)

    def new_rack(self):
        # kill the GI again
        self.game.base_game_mode.gi_toggle("OFF")
        # TODO stuff
        # if 2 balls in play - add one
        # if 3 balls in play - run ball save
        # play the interstitial animation
        # load up the lightning
        anim = dmd.Animation().load(ep.DMD_PATH+'cloud-lightning.dmd')
        # math out the wait
        myWait = len(anim.frames) / 10.0
        # set the animation
        animLayer = ep.EP_AnimatedLayer(anim)
        animLayer.hold=True
        animLayer.frame_time = 6
        # keyframe sounds
        animLayer.add_frame_listener(2,self.game.play_remote_sound,param=self.game.assets.sfx_lightning1)
        animLayer.add_frame_listener(2,self.lightning,param="top")
        animLayer.add_frame_listener(3,self.lightning,param="left")
        animLayer.add_frame_listener(6,self.game.play_remote_sound,param=self.game.assets.sfx_lightning2)
        animLayer.add_frame_listener(6,self.lightning,param="top")
        animLayer.add_frame_listener(7,self.lightning,param="left")
        animLayer.add_frame_listener(10,self.game.play_remote_sound,param=self.game.assets.sfx_lightningRumble)
        animLayer.add_frame_listener(10,self.lightning,param="top")
        animLayer.add_frame_listener(11,self.lightning,param="right")
        # turn it on
        self.layer = animLayer
        self.delay(delay=myWait,handler=self.new_rack_pan)


    def new_rack_pan(self):
        # turn the GI back on here
        self.game.base_game_mode.gi_toggle("ON")
        # setup the pan script
        script =[]
        for i in range(0,-52,-1):
            print "PAN i VALUE: " + str(i)
            showdownStill = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(ep.DMD_PATH+'town-pan.dmd').frames[0])
            showdownStill.set_target_position(0,i)
            if i == -51:
                time = 1
            else:
                time = 0.015
            script.append({'seconds':time,'layer':showdownStill})
        showdownPan = dmd.ScriptedLayer(128,32,script)
        self.layer = showdownPan
        self.delay(delay=1.5,handler=self.new_rack_display)

    def new_rack_display(self):
        # if 2 balls are in play add another
        if self.game.num_balls_in_play == 2:
            self.add_ball()
            self.game.interrupter.ball_added()
        # if 3 balls are already in play
        elif self.game.num_balls_in_play == 3:
            self.game.ball_save.start(num_balls_to_save=1, time=10, now=True, allow_multiple_saves=False)
            self.game.interrupter.ball_save_activated()
        # this is where to show "ball added" or "ball saver on"
        self.new_rack_finish()

    def new_rack_finish(self):
            # reset the dudes
        self.showdown_reset_guys()

    def lightning(self,section):
        # set which section of the GI to flash
        if section == 'top':
            lamp = self.game.base_game_mode.giLamps[0]
        elif section == 'right':
            lamp = self.game.base_game_mode.giLamps[1]
        elif section == 'left':
            lamp = self.game.base_game_mode.giLamps[2]
        else:
            pass
        # then flash it
        lamp.pulse(216)

    def setup_targets(self):
        # pop up the targets
        for i in range(0,4,1):
            self.target_up(i)

    def showdown_reset_guys(self):
        # pop up all the targets
        self.setup_targets()
        # then reset the display
        self.guyLayers = []
        self.badGuy0 = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(ep.DMD_PATH+'dude-gets-shot-full-body.dmd').frames[0])
        self.badGuy0.set_target_position(-49,0)
        self.badGuy0.composite_op = "blacksrc"
        self.guyLayers.append(self.badGuy0)
        self.badGuy1 = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(ep.DMD_PATH+'dude-gets-shot-full-body.dmd').frames[0])
        self.badGuy1.set_target_position(-16,0)
        self.badGuy1.composite_op = "blacksrc"
        self.guyLayers.append(self.badGuy1)
        self.badGuy2 = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(ep.DMD_PATH+'dude-gets-shot-full-body.dmd').frames[0])
        self.badGuy2.set_target_position(15,0)
        self.badGuy2.composite_op = "blacksrc"
        self.guyLayers.append(self.badGuy2)
        self.badGuy3 = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(ep.DMD_PATH+'dude-gets-shot-full-body.dmd').frames[0])
        self.badGuy3.set_target_position(47,0)
        self.badGuy3.composite_op = "blacksrc"
        self.guyLayers.append(self.badGuy3)
        combined = dmd.GroupedLayer(128,32,self.guyLayers)
        combined.composite_op = "blacksrc"
        self.layer = combined

    def showdown_hit(self,target):
        # handle a guy hit in a showdown
        print "KILLING GUY: " + str(target)
        # count the dead guy
        self.deathTally += 1
        # score points
        # after the 4th guy the point value goes up
        if self.deathTally > 4:
            self.showdownValue = 450000
        self.game.score(self.showdownValue)

        # swap out the appropriate layer
        shotguy = dmd.Animation().load(ep.DMD_PATH+'dude-gets-shot-full-body.dmd')
        if target == 0:
            # take out the current hit guy
            self.guyLayers.remove(self.badGuy0)
            self.badGuy0 = dmd.AnimatedLayer(frames=shotguy.frames,hold=True,opaque=False,repeat=False,frame_time=6)
            self.badGuy0.set_target_position(-49,0)
            self.badGuy0.composite_op = "blacksrc"
            # append on the new layer to the end to put it in the front
            self.guyLayers.append(self.badGuy0)
        elif target == 1:
            # take out the current hit guy
            self.guyLayers.remove(self.badGuy1)
            self.badGuy1 = dmd.AnimatedLayer(frames=shotguy.frames,hold=True,opaque=False,repeat=False,frame_time=6)
            self.badGuy1.set_target_position(-16,0)
            self.badGuy1.composite_op = "blacksrc"
            # append on the new layer to the end to put it in the front
            self.guyLayers.append(self.badGuy1)
        elif target == 2:
            # take out the current hit guy
            self.guyLayers.remove(self.badGuy2)
            self.badGuy2 = dmd.AnimatedLayer(frames=shotguy.frames,hold=True,opaque=False,repeat=False,frame_time=6)
            self.badGuy2.set_target_position(15,0)
            self.badGuy2.composite_op = "blacksrc"
            # append on the new layer to the end to put it in the front
            self.guyLayers.append(self.badGuy2)
        else:
            # take out the current hit guy
            self.guyLayers.remove(self.badGuy3)
            self.badGuy3 = dmd.AnimatedLayer(frames=shotguy.frames,hold=True,opaque=False,repeat=False,frame_time=6)
            self.badGuy3.set_target_position(47,0)
            self.badGuy3.composite_op = "blacksrc"
            # append on the new layer to the end to put it in the front
            self.guyLayers.append(self.badGuy3)

        myWait = len(shotguy.frames) / 10.0
        # put the new layer  in place
        combined = dmd.GroupedLayer(128,32,self.guyLayers)
        combined.composite_op = "blacksrc"
        self.layer = combined
        # play a shot sound
        self.game.sound.play(self.game.assets.sfx_gunfightShot)
        # if the 4 dudes are dead, reset them
        myWait = len(shotguy.frames) / 10.0
        if self.deathTally % 4 == 0:
            print "THEY'RE ALL DEAD JIM"
            self.delay(delay=myWait,handler=self.new_rack)
        else:
            self.delay(delay=myWait,handler=self.game.interrupter.showdown_hit,param=self.showdownValue)

        ## a way out for now
        #if self.deathTally >= 8:
        #    self.end_showdown()

    def end_showdown(self):
        #derp
        # kill the music
        self.game.sound.stop_music()
        # tally some score?
        # play a quote about bodycount
        bodycount = self.game.show_tracking('showdownTotal')
        # if the total for this round of showdown was higher stored, store it
        if self.deathTally > bodycount:
            self.game.set_tracking('showdownTotal',self.deathTally)
        # and reset the death tally
        self.deathTally = 0
        # see if the death tally beats previous/existing and store in tracking if does - for showdown champ
        # reset the quickdraw status of the bad guys
        for i in range(0,2,1):
            print "END SHOWDOWN QUICKDRAWS: " + str(i)
            self.game.set_tracking('quickdrawStatus',False,i)
        # turn off lights
        for i in range(0,4,1):
            print "END SHOWDOWN BAD GUYS " + str(i)
            self.game.set_tracking('badGuysDead',i,False)
        # drop all teh targets
        for coil in self.coils:
            coil.disable()
        # reset the badguy UP tracking just in case
        for i in range (0,4,1):
            self.game.set_tracking('badGuyUp',i,False)
        # tracking - turn it back to open
        self.game.set_tracking('quickdrawStatus',"OPEN",self.side)
        # start up the main themse again
        self.game.base_game_mode.music_on()
        # unload
        self.game.modes.remove(self.game.bad_guys)

    ###
    ###   ____              __ _       _     _
    ###  / ___|_   _ _ __  / _(_) __ _| |__ | |_
    ### | |  _| | | | '_ \| |_| |/ _` | '_ \| __|
    ### | |_| | |_| | | | |  _| | (_| | | | | |_
    ###  \____|\__,_|_| |_|_| |_|\__, |_| |_|\__|
    ###                          |___/
    ###


    def start_gunfight(self,side):
        self.game.set_tracking('lampStatus',"OFF")
        self.game.update_lamps()
        if side == 0:
            self.game.lamps.leftGunfightPin.schedule(0x00FF00FF)
        else:
            self.game.lamps.rightGunfightPin.schedule(0x00FF00FF)
        self.game.increase_tracking('gunfightsStarted')
        print "GUNFIGHT GOES HERE"
        # pop up the post
        print "RAISE POST ON SIDE: " + str(side)
        self.activeSide = side
        self.posts[self.activeSide].patter(on_time=4,off_time=12,original_on_time=30)
        # set the bad guy pop order accounting for the side it started on
        badGuys = [0,1,2,3]
        # select our eventual target
        # 0 is the left side, it shouldn't use target 1
        if side == 0:
            enemy = random.randrange(1,3,1)
        # 1 is the right side, it shouldn't use target 3
        else:
            enemy = random.randrange(0,2,1)
        # scramble the list
        random.shuffle(badGuys)
        # pull out the enemey
        print "ENEMY: " + str(enemy)
        print badGuys
        badGuys.remove(enemy)
        # and tag them on the end
        badGuys.append(enemy)
        print badGuys
        # stop the music
        print "START GUNFIGHT IS KILLING THE MUSIC"

        self.game.sound.stop_music()
        # play the intro riff
        myWait = self.game.sound.play(self.game.assets.music_gunfightIntro)
        # delayed play the drum roll
        self.delay(delay=myWait,handler=self.game.play_remote_music,param=self.game.assets.music_drumRoll)
        # play a quote
        self.game.sound.play_voice(self.game.assets.quote_gunfightStart)
        # display the clouds with gunfight text
        title = dmd.TextLayer(64, 5, self.game.assets.font_20px_az, "center", opaque=False).set_text("Gunfight")
        title.composite_op = "blacksrc"
        backdrop = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(ep.DMD_PATH+'gunfight-top.dmd').frames[0])
        mask = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(ep.DMD_PATH+'gunfight-mask.dmd').frames[0])
        mask.composite_op = "blacksrc"
        self.layer = dmd.GroupedLayer(128,32,[backdrop,mask,title])
        # after a delay pan down to the dude
        self.delay(name="pan",delay = 1.5,handler=self.gunfight_pan,param=badGuys)

    def gunfight_won(self):
        print "GUNFIGHT WON IS KILLING THE MUSIC"
        self.game.sound.stop_music()
        # cancel the lose delay
        self.cancel_delayed("Gunfight Lost")
        # play a quote
        self.game.sound.play(self.game.assets.sfx_gunfightShot)
        self.delay(delay=0.2,handler=self.game.play_remote_sound,param=self.game.assets.sfx_gunfightFlourish)
        self.delay(delay=0.3,handler=self.game.play_remote_sound,param=self.game.assets.quote_gunWin)
        # play the animation
        anim = dmd.Animation().load(ep.DMD_PATH+'dude-gets-shot-shoulders-up.dmd')
        myWait = len(anim.frames) / 10.0
        animLayer = dmd.AnimatedLayer(frames=anim.frames,hold=True,opaque=True,repeat=False,frame_time=6)
        self.layer = animLayer
        # after the animation, display the win
        self.delay(delay=myWait,handler=self.gunfight_display_win)

    def gunfight_display_win(self):
        # set some tracking
        self.game.increase_tracking('gunfightsWon')
        # up the rank if it's not full yet
        if self.game.show_tracking('rank') < 4:
            newrank = self.game.increase_tracking('rank')
        # if it is full, this bit is awkward
        else:
            newrank = 4
        ranks = ["STRANGER", "PARTNER", "DEPUTY", "SHERIFF", "MARSHAL"]
        textString3 = "YOUR RANK: " + ranks[newrank]
        values = ["500,000","750,000","1,000,000","1,500,000","2,000,000"]
        textString4 = "QUICKDRAWS WORTH: " + values[newrank]
        # award some points
        points = 750000
        self.game.score(points)
        # show the win screen
        textLine1 = dmd.TextLayer(64, 0, self.game.assets.font_7px_bold_az, "center", opaque=False).set_text("BAD GUY SHOT!")
        textLine2 = ep.pulse_text(self,64,9,ep.format_score(points))
        textLine3 = dmd.TextLayer(64, 20, self.game.assets.font_5px_AZ, "center", opaque=False).set_text(textString3)
        textLine4 = dmd.TextLayer(64, 26, self.game.assets.font_5px_AZ, "center", opaque=False).set_text(textString4)
        self.layer = dmd.GroupedLayer(128,32,[textLine1,textLine2,textLine3,textLine4])
        self.delay(delay=2,handler=self.end_gunfight)

    def gunfight_lost(self):
        # drop the bad guy
        self.target_down(self.enemy)
        print "GUNFIGHT LOST IS KILLING THE MUSIC"
        self.game.sound.stop_music()
        # play a quote
        self.game.sound.play_voice(self.game.assets.quote_gunFail)
        # shut things down
        self.end_gunfight()

    def end_gunfight(self):
        self.layer = None
        # turn off some lights?
        self.game.set_tracking('lampStatus', "ON")
        self.game.update_lamps()
        # tidy up - set the gunfight status and bart brothers status to open
        self.game.set_tracking('gunfightStatus',"OPEN")
        self.game.set_tracking('bartStatus',"OPEN")
        # turn the main game music back on
        self.game.base_game_mode.music_on()
        # unload the mode
        self.game.modes.remove(self.game.bad_guys)

    def gunfight_pan(self,badGuys):
        # the intro animation
        anim = dmd.Animation().load(ep.DMD_PATH+'gunfight-pan.dmd')
        myWait = len(anim.frames) / 60 + 1.3
        animLayer = dmd.AnimatedLayer(frames=anim.frames,hold=True,opaque=True,repeat=False,frame_time=1)
        self.layer = animLayer
        self.delay(name="eyes",delay=myWait,handler=self.gunfight_intro_eyes,param=badGuys)

    def gunfight_intro_eyes(self,badGuys):
        # pop up the first bad guy and remove it from the array
        enemy = badGuys.pop(0)
        print "POP ENEMY: " + str(enemy)
        self.target_up(enemy)
        # play the orchestra hit sound
        self.game.sound.play(self.game.assets.sfx_gunfightHit1)
        # show the eyes animation
        anim = dmd.Animation().load(ep.DMD_PATH+'gunfight-eyes.dmd')
        myWait = len(anim.frames) / 10.0
        animLayer = dmd.AnimatedLayer(frames=anim.frames,hold=True,opaque=True,repeat=False,frame_time=6)
        self.layer = animLayer
        # after a delay pass to the hands with the pop order
        self.delay(name="hands",delay=1.1,handler=self.gunfight_intro_hands,param=badGuys)
        # and drop the current one
        self.delay(delay=1.1,handler=self.target_down,param=enemy)

    def gunfight_intro_hands(self,badGuys):
        # pop the second bad guy and remove it
        enemy = badGuys.pop(0)
        print "POP ENEMY: " + str(enemy)
        self.target_up(enemy)
        self.game.sound.play(self.game.assets.quote_gunfightReady)
        # play the second orchestra hit
        self.game.sound.play(self.game.assets.sfx_gunfightHit2)
        # show the hands animation
        anim = dmd.Animation().load(ep.DMD_PATH+'gunfight-hands.dmd')
        myWait = len(anim.frames) / 10.0
        animLayer = dmd.AnimatedLayer(frames=anim.frames,hold=True,opaque=True,repeat=False,frame_time=6)
        self.layer = animLayer
        # after a delay pass to the feet with the pop order
        self.delay(name="boots",delay=1.1,handler=self.gunfight_intro_boots,param=badGuys)
        self.delay(delay=1.1,handler=self.target_down,param=enemy)

    def gunfight_intro_boots(self,badGuys):
        # pop the third bad guy
        enemy = badGuys.pop(0)
        print "POP ENEMY: " + str(enemy)
        self.target_up(enemy)
        self.game.sound.play(self.game.assets.quote_gunfightSet)
        # play the orchestra hit
        self.game.sound.play(self.game.assets.sfx_gunfightHit3)
        # show the boots
        boots = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(ep.DMD_PATH+'gunfight-boots.dmd').frames[0])
        self.layer = boots
        # after a delay - pass to the final setp
        self.delay(name="draw",delay=1.1,handler=self.gunfight_intro_draw,param=badGuys)
        self.delay(delay=1.1,handler=self.target_down,param=enemy)

    def gunfight_intro_draw(self,badGuys):
        # pop the last bad guy
        enemy = badGuys.pop(0)
        print "POP ENEMY: " + str(enemy)
        # need this for the lost
        self.enemy = enemy
        self.target_up(enemy)
        # play the 4 bells
        self.game.sound.play(self.game.assets.sfx_gunfightBell)
        self.delay(delay=0.6,handler=self.game.play_remote_sound,param=self.game.assets.sfx_gunCock)
        # run the animation
        anim = dmd.Animation().load(ep.DMD_PATH+'gunfight-boots.dmd')
        myWait = len(anim.frames) / 10.0
        animLayer = dmd.AnimatedLayer(frames=anim.frames,hold=True,opaque=True,repeat=False,frame_time=6)
        self.layer = animLayer
        # pass one last time to the release
        self.delay(name="release",delay=myWait,handler=self.gunfight_release)

    def gunfight_release(self):
        # play the draw quote
        self.game.sound.play(self.game.assets.quote_gunfightDraw)
        # relase the post - hm. no way to know which one is up Oops. # todo fix that later
        text = dmd.TextLayer(28,8,self.game.assets.font_12px_az,"center",opaque=False).set_text("DRAW!",blink_frames=2)
        backdrop = dmd.FrameLayer(opaque=False, frame=dmd.Animation().load(ep.DMD_PATH+'gunfight-boots.dmd').frames[8])
        self.layer = dmd.GroupedLayer(128,32,[backdrop,text])
        # turn the GI back on
        self.game.set_tracking('lampStatus', "ON")
        self.game.update_lamps()
        # and turn on target guy
        self.lights[self.enemy].enable()
        print "DROP THE POST"
        self.posts[self.activeSide].disable()
        # set a named timer for gunfight lost
        self.delay(name="Gunfight Lost",delay=4,handler=self.gunfight_lost)


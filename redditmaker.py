import moviepy.editor as mp
import moviepy.audio.fx.all as afx
import moviepy.video.fx.all as vfx
import numpy as np
import pandas as pd
import sys
from pathlib import Path
import shutil

import os

from gtts import gTTS

import soundfile as sf

import random
import praw
import pprint
import re
import textwrap

subRedName = "AskReddit"

# These are words that youtube can think are bad, so the
# voiceover and preview text get replaced with alternatives.
# Also, unreadable things like f*ck with an asterisk need to
# be replaced because the text to speech will not read it correctly.
badWords = ["f*ck", "fuck", "f*cking", "fucking", "$hit", "shit", "shitty", "shitting", "ass", "hell", "bitch", "tit", "boob"]
gdeWords = ["fork", "fork", "forking", "forking", "short", "short", "really bad", "pooping", "butt", "heck", "ditch", "breast", "breast"]

tempFolderName = "temp" + str(random.randrange(0, 10000))

helpScreen ="""

Usage: redditmaker [options]
Options:
  -h, --help               Display this help menu
  -rn, --randomName        Output video has randomized name, this is for debug
                           purposes
  -f, --frame <number>     Only export the single frame of video specified
  -h, --hot                Specify to gather posts from the category "hot",
                           default is "hot"
  -t, --top                Specify to gather posts from the category "top",
                           default is "hot"
  -n, --new                Specify to gather posts from the category "new",
                           default is "hot"
  -lf, --lookFirst <num>   Change the amount of post titles you want to preview
                           before render, default is 20
  -i, --include <string>   Only show post titles that include a specific string
"""

# Print help screen
for a in sys.argv:
    if a.lower() == "--help":
        print(helpScreen)
        sys.exit()

# Clamp function
def clamp(num, min_value, max_value):
    return max(min(num, max_value), min_value)

# Does the string have any numbers
def containsNumber(value):
    for character in value:
        if character.isdigit():
            return True
    return False

# Automatically wrap text so it fits within the width of the video
def wrapText(val, cnt):
    outStr = ""
    wrapper = textwrap.TextWrapper(width=cnt)
    wrpArry = wrapper.wrap(text=val)
    for s in wrpArry:
        outStr += s + '\n'
    print(outStr)
    return outStr
    
# Generate file-friendly name for output
def outputName():
    for a in sys.argv:
        if a.lower() == "-rn" or a.lower() == "--randomName":
            return "out" + str(random.randrange(0, 10000))
    return commentsToSay[0].replace("\\", "").replace("/", "%").replace(" ", "_")
    
# Only export the single frame of video specified after -f
def onlyFrame():
    ac = 0
    for a in sys.argv:
        if a.lower() == "-f" or a.lower() == "--frame":
            return int(sys.argv[ac+1])
        ac += 1
    return False
    
# Specify what category to gather posts from, default is "hot"
def category():
    for a in sys.argv:
        if a.lower() == "-h" or a.lower() == "--hot":
            return "hot"
        if a.lower() == "-t" or a.lower() == "--top":
            return "top"
        if a.lower() == "-n" or a.lower() == "--new":
            return "new"
    return "hot"
    
# Specify the amount of post titles you want to preview, default is 20
def lookFirst():
    g = 0
    for a in sys.argv:
        if a.lower() == "-lf" or a.lower() == "--lookFirst":
            if len(sys.argv) > g+1:
                if sys.argv[g+1][0].isnumeric():
                    return int(sys.argv[g+1])
            return 20
        g += 1
    return 20
    
# Only show post titles that include a specific string
def include():
    g = 0
    for a in sys.argv:
        if a.lower() == "--include" or a.lower() == "-i":
            return sys.argv[g+1]
        g += 1
    return False

# Function to replace unfriendly words with their alternatives
def replaceBadWords(str):
    finalStr = ""
    
    ac = 0
    for s in str.split(" "):
        bcnt = 0
        wasBad = False
        for b in badWords:
            if s == b:
                finalStr += gdeWords[bcnt] + " "
                wasBad = True
            bcnt += 1
        if wasBad == False:
            finalStr += s + " "
    return finalStr

# Checks if selected post has already had a video made for it in outputvideos folder
def alreadyMade(postN):
    title = posts[postN].title
    supposedName = "./outputvideos/" + title.replace("\\", "").replace("/", "%").replace(" ", "_") + "__-__r%" + subRedName + "_#shorts_#reddit.mp4"
    
    for f in os.listdir("./outputvideos"):
        if supposedName == f:
            return True
    return False
  

def UploadVideo():
    import subprocess
    print('python3 upload_video.py --file="./outputvideos/' + outputName() + '__-__r%' + subRedName + '.mp4" --title="'+re.sub(r'[^\w]', ' ', commentsToSay[0].replace("\\", "")) + '  -  r/' + subRedName + '" --description="Comment your own opinion\\n\\nMusic:\\nLakey Inspired\\n\\n#shorts\\n#reddit" --category="24" --keywords="reddit,storytime,askreddit,reading,read reddit"')
    output = subprocess.run(['python3', 'upload_video.py', '--file="./outputvideos/' + outputName() + '__-__r%' + subRedName + '.mp4"', '--title="'+re.sub(r'[^\w]', ' ', commentsToSay[0].replace("\\", "")) + '  -  r/' + subRedName + '"', '--description="Comment your own opinion\n\nMusic:\nLakey Inspired\n\n#shorts\n#reddit"', '--category="24"', '--keywords="reddit,storytime,askreddit,reading,read reddit"'])


while True:
    if os.path.isdir("./pendingvoiceclips/" + tempFolderName) == False:
        os.mkdir("./pendingvoiceclips/" + tempFolderName)
    
    # All information regarding reddit, requires api to work.
    reddit = praw.Reddit(
        client_id="loongasssiiddddddddddd",
        client_secret="eveeennnlooonngggeeerrrsssecret",
        user_agent="user_name",
        username="user_name",
        password="password",
    )
    
    # Gathers post titles and add to 'posts' array
    posts = []
    if category() == "hot":
        for submission in reddit.subreddit(subRedName).hot(limit=400):
            if include() != False:
                if include().lower() in submission.title.lower():
                    posts.append(submission)
            else:
                posts.append(submission)
    elif category() == "new":
        for submission in reddit.subreddit(subRedName).new(limit=100):
            if include() != False:
                if include().lower() in submission.title.lower():
                    posts.append(submission)
            else:
                posts.append(submission)
    elif category() == "top":
        for submission in reddit.subreddit(subRedName).top(limit=400):
            if include() != False:
                if include().lower() in submission.title.lower():
                    posts.append(submission)
            else:
                posts.append(submission)
    
    if lookFirst():
        count = 0
        for post in posts:
            print(str(count) + " :: " + post.title + "\n")
            count += 1
            if count >= lookFirst():
                break
        randPostNum = int(input("\033[1;32;40mWhich number?\033[0;0m >  "))
    else:
        randPostNum = random.randrange(0, len(posts))
        if len(sys.argv) >= 3:
            if sys.argv[1] == "-r" and containsNumber(sys.argv[2]):
                randPostNum = int(sys.argv[2])
            else:
                while alreadyMade(randPostNum) == True:
                    randPostNum = random.randrange(0, len(posts))
        else:
            while alreadyMade(randPostNum) == True:
                randPostNum = random.randrange(0, len(posts))
    
    top_level_comments = list(posts[randPostNum].comments)
        
    commentsToSay = []
    commentsToSay.append(posts[randPostNum].title)
    print("Num: " + str(randPostNum) + "  === " + posts[randPostNum].title + " ===\n")
    for comment in top_level_comments:
        try:
            # Make sure the comment is small enough to fit on the screen when wrapped
            if len(commentsToSay) < 30 and len(commentsToSay) < len(top_level_comments)-2 and len(comment.body) < 250 and comment.body != "[removed]"  and comment.body != "[deleted]":
                commentsToSay.append(comment.body)
                print(comment.body)
        except:
            print("Invalid comment")
            break
    
    print("\n")
    
    # Generates each voiceover and saves to file in pendingvoiceclips/
    i = 0
    for comment in commentsToSay:
        language = 'en'
        myobj = gTTS(text=replaceBadWords(comment.replace("/", " slash ").replace("\\", " slash ")), lang=language, slow=False)
        myobj.save("./pendingvoiceclips/" + tempFolderName + "/clip" + str(i) + ".wav")
        print("Recording voice clips: " + str(round((i/len(commentsToSay))*100, 2)) + "%", end='\r', flush=True)
        i += 1
    print("")
    
    totalDuration = 0
    voiceOvers = []
    filenames = os.listdir("./pendingvoiceclips/" + tempFolderName)
    i = 0
    for clip in filenames:
        if totalDuration + mp.AudioFileClip("./pendingvoiceclips/" + tempFolderName + "/clip" + str(i) + ".wav").duration + 0.5 < 60:
            voiceOvers.append(mp.AudioFileClip("./pendingvoiceclips/" + tempFolderName + "/clip" + str(i) + ".wav"))
            totalDuration += mp.AudioFileClip("./pendingvoiceclips/" + tempFolderName + "/clip" + str(i) + ".wav").duration + 0.5
            print(totalDuration)
            i+=1
    
    # Warn if the video length is too short
    if totalDuration < 45:
        continuePromptAnswer = input("\033[1;31;40mTotal duration is less than 45s. Continue?\033[0;0m Y/n>  ")
        if continuePromptAnswer.upper() != "Y" and continuePromptAnswer.upper() != "YES":
            continue
    
    # Load premade clips
    randMusic = random.randrange(1, 3 + 1)
    music = mp.AudioFileClip("backgroundMusic" + str(randMusic) + ".mp3").fx(afx.volumex, 0.12)
    randTemplate = random.randrange(1, 2 + 1)
    template = mp.VideoFileClip("Mobile-Short-Template" + subRedName + str(randTemplate) + ".mp4")
    transition = mp.VideoFileClip("TransitionReddit.mp4")
    background = (mp.ImageClip("redditPostBknd.png")
                .set_duration(1)
                .set_position(("center", "center")))
    background.resize((550,1100))
    
    w = 1080
    h = 2160
    screenSize = (w,h)
    backgroundSize = background.size
    
    # Create intro, where the post title is read
    final_output = template.subclip(0, voiceOvers[0].duration)
    final_output.audio = voiceOvers[0]
    final_output.resize((w,h))
    bknd = background
    bknd = bknd.resize((1000, (wrapText(commentsToSay[0], 20).count('\n')+1) * 100 + 10))
    txt_clip = mp.TextClip(wrapText(commentsToSay[0], 20), font='./fonts/IBMPlexSans-Regular.ttf', color = 'white', align="West", size=(backgroundSize[0], None), fontsize=80, method='caption').set_duration(voiceOvers[0].duration).set_position(("left", "top")).margin(40, opacity=0)
    bknd = bknd.set_duration(voiceOvers[0].duration)
    bknd = mp.CompositeVideoClip([bknd, txt_clip]).set_position(('center', 'center')).set_duration(voiceOvers[0].duration)
    final_output = mp.CompositeVideoClip([final_output, bknd])
    
    
    allCompletedVideoClips = []
    
    # For each voice clip create a part of the video and append it to the main video
    i = 0
    for clip in voiceOvers:
        if i != 0 and final_output.duration < 60:
            t = template
            videoportion = t.subclip(final_output.duration, final_output.duration + voiceOvers[i].duration)
            videoportion.duration = voiceOvers[i].duration
            
            bknd = background
            bknd = bknd.resize((1000, (wrapText(commentsToSay[i], 30).count('\n')+1) * 80 + 20))
            
            # Generate a text clip containing comment text
            txt_clip = mp.TextClip(wrapText(commentsToSay[i], 30), font='./fonts/IBMPlexSans-Regular.ttf', color = 'white', align="West", size=(backgroundSize[0], None), fontsize=60, method='caption').set_duration(voiceOvers[i].duration).set_position(("left", "top")).margin(50, opacity=0)
            
            bknd = bknd.set_duration(clip.duration)
            bknd = mp.CompositeVideoClip([bknd, txt_clip]).set_position(('center', 'center')).set_duration(clip.duration)
            
            #subredditText = mp.TextClip("r/" + subRedName, font='./fonts/VAG Rounded Regular.ttf', stroke_color='black', stroke_width=4, color = 'white', size=(w, None), fontsize=90, method='label').set_duration(videoportion.duration + transition.duration).set_position(("center", "top")).margin(200, opacity=0)
            videoportion = mp.CompositeVideoClip([videoportion, bknd])
            videoportion.audio = voiceOvers[i]
            
            allCompletedVideoClips.append(videoportion)
            allCompletedVideoClips.append(transition)
        i += 1
    
    joinedClips = mp.concatenate_videoclips(allCompletedVideoClips)
    final_output = mp.concatenate_videoclips([final_output, joinedClips])
    
    final_output.audio = mp.CompositeAudioClip([final_output.audio, music.subclip(0, final_output.duration)])
    
    if onlyFrame() == False:
        final_output.write_videofile("./outputvideos/" + outputName() + "__-__r%" + subRedName + ".mp4", codec='libx264')
    else:
        final_output.save_frame("frame.png", t = onlyFrame())
    
    # Deletes temp voicefiles
    shutil.rmtree("./pendingvoiceclips/" + tempFolderName)
    
    # Print large green square to indicate that render is over. Useful for when afk
    print("\033[1;32;40m█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████\033[0;0m")
    
    keepWorkingAnswer = input("\033[1;31;40mMake another video?\033[0;0m Y/n>  ")
    if keepWorkingAnswer.upper() == "N" or keepWorkingAnswer.upper() == "NO":
        break

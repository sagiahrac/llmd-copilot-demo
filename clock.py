import subprocess


def open_clock_app(delay: float = 1.0):
    applescript = '''
    tell application "Clock"
        activate
    end tell
    '''

    if delay > 0:
        applescript += f"\ndelay {delay} -- Wait for the app to open\n"
    
    subprocess.run(["osascript", "-e", applescript])

def reset_stopwatch():
    applescript = '''
    tell application "System Events"
        tell application process "Clock"
            tell window "Clock"
                -- 1. Click the 3rd radio button (Stopwatch)
                click radio button 3 of radio group 1 of toolbar 1

                tell group 1 of group 1 of group 1 of group 1 of group 1
                    tell group 2
                        tell group 1 of group 1 of group 1 of group 1 of group 1
                            click button 1
                        end tell
                    end tell
                end tell
            end tell
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", applescript])

def stopwatch_start_stop():
    applescript = '''
    tell application "System Events"
        tell application process "Clock"
            tell window "Clock"
                -- 1. Click the 3rd radio button (Stopwatch)
                click radio button 3 of radio group 1 of toolbar 1

                tell group 1 of group 1 of group 1 of group 1 of group 1
                    tell group 2
                        tell group 1 of group 1 of group 1 of group 1 of group 1
                            click button 2
                        end tell
                    end tell
                end tell
            end tell
        end tell
    end tell
    '''
    subprocess.run(["osascript", "-e", applescript])

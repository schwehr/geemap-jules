import os
import tempfile
import shutil
import subprocess

# Standalone reproduction of the FIXED function logic
def gif_to_png_fixed(in_gif, out_dir=None, prefix="", verbose=True):
    in_gif = os.path.abspath(in_gif)

    if out_dir is None:
        out_dir = tempfile.mkdtemp()

    if not os.path.exists(out_dir):
        os.makedirs(out_dir)

    out_dir = os.path.abspath(out_dir)
    # New secure implementation using a list of arguments
    args = [
        "ffmpeg",
        "-loglevel",
        "error",
        "-i",
        in_gif,
        "-vsync",
        "0",
        f"{out_dir}/{prefix}%d.png",
    ]
    print(f"Executing with subprocess.run: {args}")
    try:
        # We expect this to fail if ffmpeg is missing, but not execute the 'touch' command
        subprocess.run(args, check=True, capture_output=True, text=True)
    except FileNotFoundError:
        print("ffmpeg not found, as expected in this environment.")
    except subprocess.CalledProcessError as e:
        print(f"Subprocess failed as expected: {e}")
    except Exception as e:
        print(f"Caught unexpected exception: {e}")

# Create a dummy gif file
with open("dummy.gif", "wb") as f:
    f.write(b"GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\xff\xff\xff!\xf9\x04\x01\x00\x00\x00\x00,\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x02D\x01\x00;")

# Try to exploit via prefix
exploit_prefix = "out; touch pwned_fixed; "
gif_to_png_fixed("dummy.gif", out_dir="out_dir_fixed", prefix=exploit_prefix)

if os.path.exists("pwned_fixed"):
    print("VULNERABILITY STILL PRESENT!")
    os.remove("pwned_fixed")
else:
    print("VULNERABILITY SUCCESSFULLY FIXED: 'pwned_fixed' file NOT created.")

# Clean up
if os.path.exists("dummy.gif"):
    os.remove("dummy.gif")
if os.path.exists("out_dir_fixed"):
    shutil.rmtree("out_dir_fixed")

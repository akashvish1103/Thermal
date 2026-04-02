import subprocess

def convert_wmv_to_mp4(input_path, output_path):
    command = [
        "ffmpeg",
        "-i", input_path,
        "-vcodec", "libx264",   # video codec
        "-acodec", "aac",       # audio codec
        output_path
    ]
    
    subprocess.run(command, check=True)
    print("Conversion completed!")



input_wmv = r"D:\Lie Detection Data HTI\Lie_detection_ex2\Thermal_lie_detection_ex2\grey_manual\krishna_grey_manual1.wmv"
# Example
convert_wmv_to_mp4(input_wmv,r"C:\Users\Akash Vishwakarma\Desktop\Thermal_Analysis\linear_mapping\output.mp4")


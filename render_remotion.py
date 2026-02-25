import json
import os
import subprocess

def render_remotion_video(slides_dict_list, project_id):
    podio_dir = os.path.abspath(os.path.join(os.getcwd(), "../podio-ai"))
    
    # Calculate duration in frames
    total_frames = sum([int(max(150, (slider.get('duration') or 5) * 30)) for slider in slides_dict_list])
    if total_frames <= 0:
        total_frames = 150
        
    props = json.dumps({"slides": slides_dict_list})
    
    output_dir = os.getenv("MEDIA_DIR", os.path.join(os.getcwd(), "outputs"))
    os.makedirs(output_dir, exist_ok=True)
    
    output_mp4 = os.path.abspath(os.path.join(output_dir, f"{project_id}.mp4"))
    
    print(f"Running Remotion render... total frames: {total_frames}")
    # Write props to a file to avoid command-line length limits
    props_path = os.path.abspath(os.path.join(output_dir, f"{project_id}_props.json"))
    with open(props_path, "w") as f:
        f.write(props)
        
    cmd = [
        "npx", "remotion", "render", 
        "app/remotion/index.ts", "SlideVideo", 
        output_mp4,
        "--props", props_path
    ]
    
    try:
        subprocess.run(cmd, cwd=podio_dir, check=True)
        return output_mp4
    except subprocess.CalledProcessError as e:
        print(f"Error rendering video: {e}")
        raise e

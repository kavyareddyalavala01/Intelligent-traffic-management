import streamlit as st
import time
from PIL import Image
from ultralytics import YOLO

# Load YOLOv8 model
model_path = "D:/Downloads/yolov8_model.pt"
model = YOLO(model_path)

def detect_ambulance(image):
    """Detect if an ambulance is present in the uploaded image."""
    img = Image.open(image)
    results = model(img)
    class_ids = results[0].boxes.cls.cpu().numpy()
    class_names = results[0].names
    detected_classes = [class_names[int(cls)].lower() for cls in class_ids]
    return "ambulance" in detected_classes

def display_traffic_signal_box(road_name, color, timer, light_placeholder, uploaded_image=None):
    """Display a traffic signal in a styled box with the traffic light, timer, and uploaded image."""
    colors = {"Red": "#FF0000", "Yellow": "#FFFF00", "Green": "#00FF00", "Off": "#333333"}

    col1, col2 = light_placeholder.columns([2, 1]) #create 2 columns, one for signal one for image.

    with col1:
        col1.markdown(
            f"""
            <div style="width: 150px; height: 400px; border: 2px solid #cccccc; border-radius: 10px; background-color: white;
                        text-align: center; box-shadow: 0px 4px 8px rgba(0, 0, 0, 0.2); margin: 10px; display: inline-block;">
                <h4 style="margin: 10px 0; font-size: 1rem; color: #333;">{road_name}</h4>
                <div style="width: 80px; height: 200px; background-color: black; border: 4px solid #222222; border-radius: 20px;
                            margin: 10px auto; display: flex; flex-direction: column; justify-content: space-around;
                            align-items: center; padding: 10px;">
                    <div style="width: 50px; height: 50px; background-color: {'#FF0000' if color == 'Red' else colors['Off']};
                                        border-radius: 50%; box-shadow: 0 0 15px {'#FF0000' if color == 'Red' else '#000000'};"></div>
                    <div style="width: 50px; height: 50px; background-color: {'#FFFF00' if color == 'Yellow' else colors['Off']};
                                        border-radius: 50%; box-shadow: 0 0 15px {'#FFFF00' if color == 'Yellow' else '#000000'};"></div>
                    <div style="width: 50px; height: 50px; background-color: {'#00FF00' if color == 'Green' else colors['Off']};
                                        border-radius: 50%; box-shadow: 0 0 15px {'#00FF00' if color == 'Green' else '#000000'};"></div>
                </div>
                <h2 style="margin: 10px 0; font-size: 1.5rem; color: #444;">{color}</h2>
                <h3 style="margin: 5px 0; font-size: 1.2rem; color: #777;">{timer} sec</h3>
            </div>
            """,
            unsafe_allow_html=True,
        )

    if uploaded_image:
        with col2:
            col2.image(uploaded_image, caption=f"Uploaded Image - {road_name}", width=150)

def main():
    st.set_page_config(page_title="Traffic Management with Ambulance Detection", layout="wide")
    st.title("Traffic Management System with Ambulance Detection")
    st.sidebar.header("Configuration")

    intersection_type = st.sidebar.selectbox(
        "Select Intersection Type",
        options=["2-Way Intersection", "3-Way Intersection", "4-Way Intersection"],
        index=2,
    )
    road_names = {
        "2-Way Intersection": ["Road 1", "Road 2"],
        "3-Way Intersection": ["Road 1", "Road 2", "Road 3"],
        "4-Way Intersection": ["Road 1", "Road 2", "Road 3", "Road 4"]
    }[intersection_type]

    green_duration = st.sidebar.number_input("Green Light Duration (seconds)", min_value=5, max_value=60, value=10)
    yellow_duration = st.sidebar.number_input("Yellow Light Duration (seconds)", min_value=1, max_value=10, value=3)

    st.sidebar.header("Ambulance Detection")
    uploaded_files = {road: st.sidebar.file_uploader(f"Upload image for {road}", type=["jpg", "png", "jpeg"]) for road in road_names}
    detected_lanes = []

    for road, file in uploaded_files.items():
        if file:
            if detect_ambulance(file):
                detected_lanes.append(road)

    if detected_lanes:
        st.sidebar.success(f"Ambulance detected in: {', '.join(detected_lanes)}")
    else:
        st.sidebar.info("No ambulances detected.")

    col1, col2, col3 = st.columns(3)
    with col1:
        start_button = st.button("Start Simulation")
    with col2:
        stop_button = st.button("Stop Simulation")
    with col3:
        reset_button = st.button("Reset Simulation")

    if "running" not in st.session_state:
        st.session_state.running = False

    if start_button:
        st.session_state.running = True

    if stop_button:
        st.session_state.running = False

    if reset_button:
        st.session_state.running = False
        for road in road_names:
            uploaded_files[road] = None

    traffic_placeholders = [st.empty() for _ in road_names]

    if st.session_state.running:
        total_duration = green_duration + yellow_duration

        while st.session_state.running:
            for road in detected_lanes:
                for phase, duration in [("Green", green_duration), ("Yellow", yellow_duration)]:
                    for remaining_time in range(duration, 0, -1):
                        if not st.session_state.running:
                            break
                        for road_index, road_name in enumerate(road_names):
                            color = "Green" if road_name == road and phase == "Green" else "Red"
                            timer = remaining_time if color == "Green" else 0
                            uploaded_image = Image.open(uploaded_files[road_name]) if uploaded_files[road_name] else None
                            display_traffic_signal_box(road_name, color, timer, traffic_placeholders[road_index], uploaded_image)
                        time.sleep(1)

            for current_road in range(len(road_names)):
                for phase, duration in [("Green", green_duration), ("Yellow", yellow_duration)]:
                    for remaining_time in range(duration, 0, -1):
                        if not st.session_state.running:
                            break
                        for road_index, road_name in enumerate(road_names):
                            if road_index == current_road:
                                color = phase
                                timer = remaining_time
                            else:
                                color = "Red"
                                timer = 0
                            uploaded_image = Image.open(uploaded_files[road_name]) if uploaded_files[road_name] else None
                            display_traffic_signal_box(road_name, color, timer, traffic_placeholders[road_index], uploaded_image)
                        time.sleep(1)
            for road in road_names:
                uploaded_files[road] = None

if __name__ == "__main__":
    main()
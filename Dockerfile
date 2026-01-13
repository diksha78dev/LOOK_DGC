# LOOK-DGC Docker Image
# Developed by Gopichand
FROM python:3.11-slim

# Set metadata
LABEL maintainer="Gopichand"
LABEL description="LOOK-DGC - Digital Image Forensics Toolkit"
LABEL version="1.0"

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libgl1-mesa-dev \
    libglib2.0-0 \
    libxrender1 \
    libxrandr2 \
    libxss1 \
    libxcursor1 \
    libxcomposite1 \
    libasound2 \
    libxi6 \
    libxtst6 \
    libxcb1 \
    libxcb-xinerama0 \
    libxcb-cursor0 \
    libfontconfig1 \
    libfreetype6 \
    libxkbcommon-x11-0 \
    x11-apps \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first for better caching
COPY gui/requirements.txt ./gui/

# Install Python dependencies
RUN pip install --no-cache-dir -r gui/requirements.txt

# Install additional dependencies for image processing
RUN pip install --no-cache-dir \
    torch torchvision --index-url https://download.pytorch.org/whl/cpu

# Copy application files
COPY gui/ ./gui/
COPY launch_look_dgc.py .

# Create directories
RUN mkdir -p ./logo/ ./images/ ./screenshots/ ./output/

# Set environment variables for GUI
ENV QT_QPA_PLATFORM=xcb
ENV QT_X11_NO_MITSHM=1
ENV DISPLAY=:0

# Create a non-root user
RUN useradd -m -s /bin/bash lookdgc
RUN chown -R lookdgc:lookdgc /app
USER lookdgc

# Expose port for potential web interface
EXPOSE 8080

# Create entrypoint script
RUN echo '#!/bin/bash\n\
echo "================================="\n\
echo "  LOOK-DGC Docker Container"\n\
echo "  Developed by: Gopichand"\n\
echo "================================="\n\
echo ""\n\
echo "To run the GUI application:"\n\
echo "  python launch_look_dgc.py"\n\
echo ""\n\
echo "Files are located in:"\n\
echo "  - Main app: /app/gui/look-dgc.py"\n\
echo "  - Launcher: /app/launch_look_dgc.py"\n\
echo ""\n\
echo "For X11 forwarding, ensure DISPLAY is set correctly"\n\
echo "Current DISPLAY: $DISPLAY"\n\
echo ""\n\
/bin/bash' > /app/start.sh && chmod +x /app/start.sh

# Set entrypoint
ENTRYPOINT ["/app/start.sh"]
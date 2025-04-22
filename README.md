# Missing-Child-Detection-System
It detect missing child . (Currently in Development)


1. pip install flask numpy opencv-python secure-smtplib geopy requests


2. Unzip sqlite+cmake.rar
3. Move sqlite and cmake folder to C drive separately.
4. Go to sqlite folder, copy the path & add the path to system variables path section.
5. Go to cmake/bin folder, copy the path & add the path to system variables path section.

6. Double click on VisualStudioSetup.exe
      During installation, select:
            6.1. In the Workloads tab, find "Desktop development with C++" build tools and check the box.
            6.2. Click on the "Individual Components" tab at the top.
                  Scroll down and select the following components:
                        6.2.1. C++ CMake Tools for Windows
                        6.2.2. Windows 10 SDK    (Any version)
                        6.2.3. MSVC v142 - VS 2019 C++ x64/x86 build tools

7. pip install dlib --no-cache-dir --verbose      (It take little much time,keep patient.)

8. pip install face_recognition --no-cache-dir

9. Run app.py  & matching.py

10. open http://127.0.0.1:5000  on your browser.

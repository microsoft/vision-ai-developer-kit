# Vision AI DevKit Postman Collection

This Postman collection export exists to faciliate changing properties, running commands, and getting information via REST calls supported by the Vision AI Camera.

To set up:

1. Import the provided collection into Postman (version 7.2.2 or higher).
1. Open the **Manage Environments** dialog (gear icon in upper, right-hand corner).
    1. **Add** a new environment.
    1. Name the environment.
    1. Add a variable named hostIp.
    1. Add a variable named sessionId.
    1. Press the **Add** button to save.

To use:

1. Determine the IP address of the camera.
    - Using an SSH connection, type `ifconfig wlan0`.
1. Select the environment you created earlier for this camera using the upper, right-hand corner dropdown box.
1. Select the **Environment quick look** button (eye icon in upper, right-hand corner).
1. Edit the current value of the hostIp variable, and type in the camera IP address obtained in step 1.
1. Open the Login request, and press the Send button.
1. In the response pane, press the Headers tab.
1. Find the **Set-Cookie** header, and copy the text after "session=".
1. Back in the **Environment quick look** dialog, set the current value for the sessionId variable to the value copied.
1. Run any of the other request. If any of the requests get an unauthorized error, re-run the Login request, copy the session Id, and update it in the Environment quick look dialog.

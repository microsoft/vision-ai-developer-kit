## Code changes
1. Don't erase the model if it is already present
2. Permission for deleting files are messed up
3. Convert twin properties to dictionary?
4. catch and handle error raised by camera config
5. Add confidence to the properties and make it settable
1. handle recovery so that the properties from the twin are loaded
1. Signal error from callback to loop so that camera client gets restarted
## Investigate
1. Reset property for model changed to false after update?
1. The documentation says that I should expect desired property updates with the desired part wrapped around them, but callbacks come back unwrapped so end up with :
    ``` 
    if "desired" in data and OBJS_OF_INTEREST_PROPERTY not data["desired"]:
        return json.loads(data["desired"][OBJS_OF_INTEREST_PROPERTY]) 
    
    if OBJS_OF_INTEREST_PROPERTY in data:
        return json.loads(data[OBJS_OF_INTEREST_PROPERTY])

## settings that work without a restart
1. ModelZipUrl ??
1. MinMessageDelaySeconds
1. ShowVideoOverlay
1. ObjectsOfInterest
1. VideoOverlayConfig
1. VideoAnalyticsEnabled ??

## settings that need a restart
1. HdmiDisplayActive
1. Bitrate ??
1. Resolution ??
1. FrameRate ??
1. ShowVideoPreview ??
1. Codec ??

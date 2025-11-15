# Student Location Troubleshooting Guide

## Error: "Location information is unavailable"

This error occurs when the browser cannot access your device's location. Here's how to fix it:

## Quick Fixes

### 1. Enable Location Services on Your Device

#### On Android:
1. Open **Settings**
2. Go to **Location** (or **Security & Location**)
3. Turn **Location** ON
4. Set mode to **High Accuracy** (uses GPS, WiFi, and mobile networks)

#### On iPhone/iPad:
1. Open **Settings**
2. Go to **Privacy** → **Location Services**
3. Turn **Location Services** ON
4. Scroll down to your browser (Safari/Chrome)
5. Select **While Using the App**

#### On Windows:
1. Open **Settings**
2. Go to **Privacy** → **Location**
3. Turn **Location** ON
4. Ensure **Allow apps to access your location** is ON

#### On Mac:
1. Open **System Preferences**
2. Go to **Security & Privacy** → **Privacy**
3. Select **Location Services**
4. Check the box next to your browser

### 2. Allow Location Access in Browser

#### Chrome:
1. Click the **lock icon** (🔒) in the address bar
2. Find **Location** permission
3. Select **Allow**
4. Refresh the page

Or:
1. Go to **Settings** → **Privacy and security** → **Site Settings**
2. Click **Location**
3. Find your site and set to **Allow**

#### Firefox:
1. Click the **lock icon** (🔒) in the address bar
2. Click **Connection secure** → **More information**
3. Go to **Permissions** tab
4. Find **Access Your Location**
5. Uncheck **Use Default** and check **Allow**

#### Safari:
1. Go to **Safari** → **Preferences** → **Websites**
2. Click **Location** in the left sidebar
3. Find your website
4. Select **Allow**

#### Edge:
1. Click the **lock icon** (🔒) in the address bar
2. Click **Permissions for this site**
3. Find **Location**
4. Select **Allow**

### 3. Check Internet Connection

Location services work better with an active internet connection:
- Ensure WiFi or mobile data is enabled
- Check that you have a stable connection
- Try moving to an area with better signal

### 4. Use a Mobile Device

If you're on a desktop/laptop without GPS:
- Location accuracy may be lower (based on WiFi/IP)
- Consider using a smartphone or tablet with GPS
- Ensure WiFi is enabled even on mobile devices (improves accuracy)

### 5. Go Outdoors

GPS works best outdoors:
- Move near a window or outside
- Avoid basements or buildings with thick walls
- Wait a few seconds for GPS to acquire signal

## Step-by-Step: First Time Setup

### For Students Using the App:

1. **Open the attendance app** in your browser
2. **Log in** with your student credentials
3. **Allow location access** when prompted
4. **Wait** for the green "Location captured" message
5. **Scan QR code** or enter the 6-digit code

### If Location Prompt Doesn't Appear:

1. Check if you previously denied location access
2. Clear site permissions:
   - Chrome: Settings → Privacy → Site Settings → Location → Remove site
   - Firefox: Settings → Privacy → Permissions → Location → Remove website
3. Refresh the page
4. Allow location when prompted again

## Common Issues

### Issue: Location is Inaccurate

**Symptoms**: Distance shows as too far even when you're in class

**Solutions**:
1. Wait 10-30 seconds for GPS to improve accuracy
2. Move closer to a window
3. Enable **High Accuracy** mode on your device
4. Restart your device
5. Clear browser cache and try again

### Issue: Location Takes Too Long

**Symptoms**: "Getting your location..." message stays for a long time

**Solutions**:
1. Check internet connection
2. Enable WiFi (even if using mobile data)
3. Move to an area with better GPS signal
4. Try refreshing the page
5. Restart your browser

### Issue: Permission Denied

**Symptoms**: "Location permission denied" error

**Solutions**:
1. Follow browser-specific instructions above
2. Check device location settings
3. Clear browser cache and cookies
4. Try a different browser
5. Restart your device

### Issue: Works on WiFi but Not on Mobile Data

**Symptoms**: Location works at home but not on campus

**Solutions**:
1. Ensure mobile data is enabled
2. Check if location services work with mobile data
3. Try enabling WiFi (even without connecting)
4. Contact your mobile carrier about location services

## Browser Compatibility

### Supported Browsers:
✅ Chrome 50+ (Recommended)
✅ Firefox 55+
✅ Safari 10+
✅ Edge 79+
✅ Samsung Internet 7+

### Not Supported:
❌ Internet Explorer
❌ Very old browser versions
❌ Browsers with JavaScript disabled

## Testing Your Location

### Quick Test:
1. Open your browser
2. Press **F12** to open Developer Tools
3. Go to **Console** tab
4. Type: `navigator.geolocation.getCurrentPosition(pos => console.log(pos), err => console.error(err))`
5. Press **Enter**
6. Allow location if prompted
7. Check the result:
   - Success: You'll see coordinates
   - Error: You'll see an error message

### Check Permission Status:
```javascript
navigator.permissions.query({name:'geolocation'}).then(result => console.log(result.state))
```
- **granted**: Location is allowed ✅
- **denied**: Location is blocked ❌
- **prompt**: Browser will ask for permission

## Still Having Issues?

### Contact Support:
If you've tried all the above and still can't access location:

1. **Take a screenshot** of the error message
2. **Note your device and browser** (e.g., "iPhone 12, Safari")
3. **Contact your instructor** or IT support
4. **Try a different device** in the meantime

### Temporary Workaround:
If location absolutely won't work:
- Inform your instructor immediately
- They may be able to manually mark your attendance
- Or provide an alternative attendance method

## Privacy & Security

### What Location Data is Used For:
- ✅ Verifying you're physically present in class
- ✅ Calculating distance from classroom
- ✅ Preventing attendance fraud

### What We DON'T Do:
- ❌ Track your location continuously
- ❌ Store your location history
- ❌ Share your location with third parties
- ❌ Use location outside of attendance marking

### Your Privacy:
- Location is only captured when you mark attendance
- You control when to share your location
- You can revoke permission anytime in browser settings
- Location data is encrypted in transit

## Technical Details

### Accuracy Requirements:
- **Required**: ≤ 100 meters accuracy
- **Typical GPS**: 5-50 meters
- **WiFi-based**: 20-100 meters
- **Cell tower**: 100-1000 meters (may be rejected)

### How It Works:
1. Browser requests location from device
2. Device uses GPS, WiFi, and cell towers
3. Location is sent to server with attendance code
4. Server calculates distance from classroom
5. Attendance is marked if within allowed radius

### Why HTTPS is Required:
- Modern browsers only allow location access on secure (HTTPS) sites
- This protects your privacy and security
- Localhost (development) is exempt from this rule

## Summary

Most location issues can be fixed by:
1. ✅ Enabling location services on your device
2. ✅ Allowing location access in your browser
3. ✅ Having a stable internet connection
4. ✅ Being outdoors or near a window
5. ✅ Using a modern browser

If problems persist, contact your instructor or IT support with details about your device and the error message you're seeing.

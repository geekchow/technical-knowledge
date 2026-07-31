# Android App bundle vs Android APK

Principle

Developers submit app bundle resources & signed key to Google Play Store.
Play Store assemble an apk according the end user's device model, locale information etc, and sign the apk with the sign key submitted by developers. 
The benifit is the end use can download a smaller package, without unnecessary resources which not suitalbe for the specific device. 
But it makes google take more control over our app, and threat to other anrdoid app distribution communities. 

Ever since Auguest 2021, the AAB format is required to submit app to Google Play.

Reference
https://www.cloudsavvyit.com/12544/apk-vs-app-bundle-why-is-google-changing-androids-app-format/

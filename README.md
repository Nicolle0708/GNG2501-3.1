import Foundation

import UserNotifications

class NotificationDelegate: NSObject, UNUserNotificationCenterDelegate {

    static var appState: AppState?

    func userNotificationCenter(

        _ center: UNUserNotificationCenter,

        didReceive response: UNNotificationResponse

    ) async {

    await MainActor.run {

        NotificationDelegate.appState?.selTab = 1

        }

    }

}

 

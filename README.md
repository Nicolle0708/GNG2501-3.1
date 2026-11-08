import SwiftUI
import UserNotifications

@main
struct ClearCue_InstructionTest_Watch_AppApp: App {
    @StateObject var appState = AppState()

    let notificationDelegate = NotificationDelegate()
    init() {
        UNUserNotificationCenter.current().delegate =
        notificationDelegate
    }
    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(appState)
                .onAppear {
                    NotificationDelegate.appState = appState
                }
        }
    }
}

 

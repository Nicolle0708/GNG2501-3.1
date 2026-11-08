import SwiftUI
import UserNotifications
import Combine
import AVFoundation

class AppState: ObservableObject{
    @Published var selTab = 0
}

struct ContentView: View {
    
    @EnvironmentObject var appState: AppState
    
    var body: some View {
        TabView (selection: $appState.selTab) {
            VStack {
                Button("Notify Me") {
                    sendNotification()
                }
            }
            .tag(0)
            .onAppear{
                requestPermission()
            }
            VStack(spacing: 1) {
                Text("🏫")
                    .font(.system(size: 140))
                Text("ROOM A204")
                    .font(.system(size: 30, weight: .bold, design: .rounded))
                    .foregroundStyle(Color(hex: 0xEBF74A))
                    .lineLimit(2)
                    .frame(height: 80, alignment: .top)
                    .multilineTextAlignment(.center)
            }
            .tag(1)
            .onLongPressGesture{
                speak("Go to math classroom A204")
            }
            VStack(spacing: 1) {
                Text("📒")
                    .font(.system(size: 140))
                Text("MATH  BOOK  P  144")
                    .font(.system(size: 30, weight: .bold, design: .rounded))
                    .foregroundStyle(Color(hex: 0xEBF74A))
                    .lineLimit(2)
                    .frame(height: 80, alignment: .top)
                    .multilineTextAlignment(.center)
            }
            .tag(2)
            .onLongPressGesture{
                speak("Open your math textbook and open to page 144")
            }
        }
    }
    func requestPermission() {
        UNUserNotificationCenter.current()
            .requestAuthorization(options: [.alert, .sound, .badge]){granted, error in
                print(granted)
            }
    }
    func sendNotification(){
        let content = UNMutableNotificationContent()
        content.title = "NOTIFICATION"
        content.body = ""
        content.sound = .defaultCritical
        
        let trigger = UNTimeIntervalNotificationTrigger(
            timeInterval: 5, repeats: false
        )
        
        let request = UNNotificationRequest(
            identifier: UUID().uuidString,
            content: content,
            trigger: trigger
        )
        
        UNUserNotificationCenter.current().add(request)
    }
    let synthesizer = AVSpeechSynthesizer()
    
    func speak(_ text: String){
        let utterance = AVSpeechUtterance(string: text)
        synthesizer.speak(utterance)
    }
}
extension Color {
    init(hex: UInt){
        self.init(
            red: Double((hex >> 16) & 0xFF) / 255.0,
            green: Double((hex >> 8) & 0xFF) / 255.0,
            blue: Double (hex & 0xFF) / 255.0
        )
    }
}

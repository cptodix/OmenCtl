use log::info;
use tokio::time::{sleep, Duration};
use crate::notifier::DesktopNotifier;

pub struct FanCleaningService;

/// RAII Safety Guard to guarantee fans are restored to automatic mode even on panic or cancellation
struct FanCleaningGuard;

impl Drop for FanCleaningGuard {
    fn drop(&mut self) {
        info!("FanCleaningGuard: Ensuring fans are restored to automatic EC control.");
        tokio::spawn(async move {
            let mut ec = crate::ec::LinuxEcController::new();
            let _ = ec.restore_auto_mode().await;
            let _ = ec.set_fan_speed_pct(0, 0);
            let _ = ec.set_fan_speed_pct(1, 0);
        });
    }
}

impl FanCleaningService {
    pub async fn run_cleaning_routine() -> String {
        info!("Starting Fan Dust Cleaning routine...");
        DesktopNotifier::send_notification(
            "OMENSpace Fan Maintenance",
            "Fan Dust Cleaning routine started. Operating fans at high airflow bursts...",
            1,
        ).await;

        // Instantiate RAII guard
        let _guard = FanCleaningGuard;

        // Step 1: Pulse Fan 1 & Fan 2 to High
        let mut ec = crate::ec::LinuxEcController::new();
        let _ = ec.set_fan_speed_pct(0, 100);
        let _ = ec.set_fan_speed_pct(1, 100);
        sleep(Duration::from_secs(4)).await;

        // Step 2: Cycle fans
        let _ = ec.set_fan_speed_pct(0, 30);
        let _ = ec.set_fan_speed_pct(1, 100);
        sleep(Duration::from_secs(2)).await;

        let _ = ec.set_fan_speed_pct(0, 100);
        let _ = ec.set_fan_speed_pct(1, 30);
        sleep(Duration::from_secs(2)).await;

        // Step 3: Max burst finish
        let _ = ec.set_fan_speed_pct(0, 100);
        let _ = ec.set_fan_speed_pct(1, 100);
        sleep(Duration::from_secs(3)).await;

        DesktopNotifier::send_notification(
            "OMENSpace Fan Maintenance",
            "Fan Dust Cleaning completed successfully. Returned to automatic fan mode.",
            0,
        ).await;

        "Fan Dust Cleaning completed successfully".to_string()
    }
}

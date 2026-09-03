use ksni::menu::{StandardItem, SubMenu};
use ksni::MenuItem;
use std::process::Command;
use log::{error, info};
use zbus::{Connection, Result as ZbusResult};

#[allow(dead_code)]
#[derive(Debug)]
struct Tray {
    power_profile: String,
    fan_mode: String,
}

impl ksni::Tray for Tray {
    fn id(&self) -> String {
        "omenspace_tray".into()
    }

    fn category(&self) -> ksni::Category {
        ksni::Category::Hardware
    }

    fn status(&self) -> ksni::Status {
        ksni::Status::Active
    }

    fn icon_name(&self) -> String {
        "omenspace".into()
    }
    
    fn title(&self) -> String {
        "OMEN SPACE".into()
    }

    fn activate(&mut self, _x: i32, _y: i32) {
        let _ = Command::new("omen-gui").spawn();
    }
    
    fn menu(&self) -> Vec<ksni::MenuItem<Self>> {
        vec![
            StandardItem {
                label: "OMENSpace'i Aç".into(),
                icon_name: "omenspace".into(),
                activate: Box::new(|_| {
                    let _ = Command::new("omen-gui").spawn();
                }),
                ..Default::default()
            }.into(),
            MenuItem::Separator,
            SubMenu {
                label: "⚡ Güç Profili".into(),
                submenu: vec![
                    StandardItem {
                        label: "🔥 Performans".into(),
                        activate: Box::new(|_| { tokio::spawn(async { set_power_profile("performance").await; }); }),
                        ..Default::default()
                    }.into(),
                    StandardItem {
                        label: "⚖️ Dengeli".into(),
                        activate: Box::new(|_| { tokio::spawn(async { set_power_profile("balanced").await; }); }),
                        ..Default::default()
                    }.into(),
                    StandardItem {
                        label: "🍃 Eko".into(),
                        activate: Box::new(|_| { tokio::spawn(async { set_power_profile("eco").await; }); }),
                        ..Default::default()
                    }.into(),
                ],
                ..Default::default()
            }.into(),
            SubMenu {
                label: "❄️ Fan Modu".into(),
                submenu: vec![
                    StandardItem {
                        label: "🤖 Otomatik".into(),
                        activate: Box::new(|_| { tokio::spawn(async { set_fan_mode("auto").await; }); }),
                        ..Default::default()
                    }.into(),
                    StandardItem {
                        label: "🌪️ Maksimum".into(),
                        activate: Box::new(|_| { tokio::spawn(async { set_fan_mode("max").await; }); }),
                        ..Default::default()
                    }.into(),
                ],
                ..Default::default()
            }.into(),
            MenuItem::Separator,
            StandardItem {
                label: "❌ Çıkış".into(),
                icon_name: "application-exit".into(),
                activate: Box::new(|_| {
                    std::process::exit(0);
                }),
                ..Default::default()
            }.into(),
        ]
    }
}

async fn get_conn() -> ZbusResult<Connection> {
    match Connection::system().await {
        Ok(c) => Ok(c),
        Err(_) => Connection::session().await,
    }
}

async fn set_power_profile(profile: &str) {
    if let Ok(conn) = get_conn().await {
        if let Err(e) = conn.call_method(
            Some("org.hp.omen"),
            "/org/hp/omen/Power",
            Some("org.hp.omen.Power"),
            "SetPowerProfile",
            &(profile)
        ).await {
            error!("Power profili değiştirilemedi: {}", e);
        } else {
            info!("Güç profili ayarlandı: {}", profile);
        }
    }
}

async fn set_fan_mode(mode: &str) {
    if let Ok(conn) = get_conn().await {
        if let Err(e) = conn.call_method(
            Some("org.hp.omen"),
            "/org/hp/omen/Fan",
            Some("org.hp.omen.Fan"),
            "SetFanMode",
            &(mode)
        ).await {
            error!("Fan modu değiştirilemedi: {}", e);
        } else {
            info!("Fan modu ayarlandı: {}", mode);
        }
    }
}

#[tokio::main]
async fn main() {
    env_logger::init();
    info!("omen-tray başlatılıyor...");
    
    let tray = Tray {
        power_profile: "balanced".into(),
        fan_mode: "auto".into(),
    };
    
    let service = ksni::TrayService::new(tray);
    let _handle = service.handle();
    service.spawn();
    
    // Uygulamayı açık tut
    loop {
        tokio::time::sleep(std::time::Duration::from_secs(3600)).await;
    }
}

import QtQuick
import QtQuick.Controls
import RinUI

Rectangle {
    id: statCard
    
    property string title: ""
    property string valueText: "0"
    property string subtitle: ""
    property string themeColor: "#2563eb"
    property string icon: "📊"
    
    width: 280
    height: 120
    radius: 12
    color: "#ffffff"
    border.color: "#e5e7eb"
    border.width: 1
    
    // 悬停效果
    HoverHandler {
        id: hoverHandler
    }
    
    Rectangle {
        anchors.fill: parent
        radius: parent.radius
        color: hoverHandler.hovered ? "#f8fafc" : "transparent"
        
        Behavior on color {
            ColorAnimation { duration: 200 }
        }
    }
    
    Row {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 16
        
        // 图标区域
        Rectangle {
            width: 60
            height: 60
            radius: 30
            color: statCard.themeColor + "20"  // 20% opacity
            anchors.verticalCenter: parent.verticalCenter
            
            Text {
                text: statCard.icon
                font.pixelSize: 24
                anchors.centerIn: parent
            }
        }
        
        // 文本信息
        Column {
            anchors.verticalCenter: parent.verticalCenter
            spacing: 4
            
            Text {
                text: statCard.title
                font.pixelSize: 14
                color: "#6b7280"
                font.weight: Font.Medium
            }
            
            Text {
                text: statCard.valueText
                font.pixelSize: 28
                font.bold: true
                color: statCard.themeColor
            }
            
            Text {
                text: statCard.subtitle
                font.pixelSize: 12
                color: "#9ca3af"
            }
        }
    }
    
    // 微妙的阴影效果
    Rectangle {
        anchors.fill: parent
        anchors.topMargin: 2
        radius: parent.radius
        color: "transparent"
        border.color: hoverHandler.hovered ? statCard.themeColor + "40" : "transparent"
        border.width: 2
        z: -1
        
        Behavior on border.color {
            ColorAnimation { duration: 200 }
        }
    }
}
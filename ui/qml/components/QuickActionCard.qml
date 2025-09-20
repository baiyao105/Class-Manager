import QtQuick 2.15
import QtQuick.Controls 2.15
import RinUI

// QuickActionCard - 快速操作卡片组件
Rectangle {
    id: quickActionCard
    
    // 卡片属性
    property string title: ""
    property string description: ""
    property string icon: ""
    property color iconColor: "#3b82f6"
    property color iconBackgroundColor: "#dbeafe"
    property bool enabled: true
    
    // 信号
    signal clicked()
    
    width: 200
    height: 120
    color: enabled ? "#ffffff" : "#f9fafb"
    radius: 12
    border.color: "#e5e7eb"
    border.width: 1
    
    // 鼠标交互
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        enabled: parent.enabled
        
        onEntered: {
            parent.color = "#f8fafc"
            parent.border.color = "#d1d5db"
        }
        
        onExited: {
            parent.color = quickActionCard.enabled ? "#ffffff" : "#f9fafb"
            parent.border.color = "#e5e7eb"
        }
        
        onClicked: {
            if (quickActionCard.enabled) {
                quickActionCard.clicked()
            }
        }
    }
    
    // 卡片内容
    Column {
        anchors.fill: parent
        anchors.margins: 16
        spacing: 12
        
        // 图标区域
        Rectangle {
            width: 48
            height: 48
            radius: 12
            color: iconBackgroundColor
            anchors.horizontalCenter: parent.horizontalCenter
            
            Text {
                text: icon
                font.pixelSize: 24
                color: iconColor
                anchors.centerIn: parent
            }
        }
        
        // 文本区域
        Column {
            width: parent.width
            spacing: 4
            
            Text {
                text: title
                font.pixelSize: 14
                font.weight: Font.Medium
                color: quickActionCard.enabled ? "#111827" : "#9ca3af"
                anchors.horizontalCenter: parent.horizontalCenter
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                width: parent.width
            }
            
            Text {
                text: description
                font.pixelSize: 12
                color: quickActionCard.enabled ? "#6b7280" : "#9ca3af"
                anchors.horizontalCenter: parent.horizontalCenter
                horizontalAlignment: Text.AlignHCenter
                wrapMode: Text.WordWrap
                width: parent.width
            }
        }
    }
    
    // 点击动画效果
    Behavior on scale {
        NumberAnimation { duration: 100; easing.type: Easing.OutCubic }
    }
    
    states: [
        State {
            name: "pressed"
            when: mouseArea.pressed && quickActionCard.enabled
            PropertyChanges { target: quickActionCard; scale: 0.98 }
        }
    ]
}
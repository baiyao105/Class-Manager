import QtQuick 2.15
import QtQuick.Controls 2.15
import RinUI 1.0

Item {
    id: navButton
    
    property string icon: ""
    property bool isSelected: false
    property bool collapsed: false
    property alias text: buttonText.text
    signal clicked()
    
    width: parent.width
    height: collapsed ? 50 : 48
    
    Rectangle {
        id: background
        anchors.fill: parent
        color: {
            if (isSelected) return "#3b82f6"
            if (mouseArea.containsMouse) return "#334155"
            return "transparent"
        }
        radius: 8
        
        Behavior on color {
            ColorAnimation { duration: 150 }
        }
    }
    
    Row {
        spacing: collapsed ? 0 : 12
        anchors.centerIn: parent
        
        // 图标
        Text {
            id: iconText
            text: icon
            font.pixelSize: collapsed ? 20 : 16
            color: {
                if (isSelected) return "#ffffff"
                if (mouseArea.containsMouse) return "#f1f5f9"
                return "#94a3b8"
            }
            anchors.verticalCenter: parent.verticalCenter
            
            Behavior on color {
                ColorAnimation { duration: 150 }
            }
        }
        
        // 文本（仅在展开时显示）
        Text {
            id: buttonText
            font.pixelSize: 14
            font.weight: isSelected ? Font.Medium : Font.Normal
            color: {
                if (isSelected) return "#ffffff"
                if (mouseArea.containsMouse) return "#f1f5f9"
                return "#cbd5e1"
            }
            anchors.verticalCenter: parent.verticalCenter
            visible: !collapsed && text !== ""
            
            Behavior on color {
                ColorAnimation { duration: 150 }
            }
        }
    }
    
    // 鼠标交互
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        onClicked: navButton.clicked()
    }
    
    // 选中指示器
    Rectangle {
        visible: isSelected && !collapsed
        width: 3
        height: parent.height * 0.6
        color: "#ffffff"
        radius: 1.5
        anchors.left: parent.left
        anchors.leftMargin: 4
        anchors.verticalCenter: parent.verticalCenter
        
        Behavior on opacity {
            NumberAnimation { duration: 150 }
        }
    }
    
    // 工具提示（仅在折叠时显示）
    ToolTip {
        visible: collapsed && mouseArea.containsMouse && buttonText.text !== ""
        text: buttonText.text
        delay: 500
        timeout: 3000
    }
}

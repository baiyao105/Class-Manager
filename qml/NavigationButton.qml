import QtQuick
import QtQuick.Controls
import RinUI

Item {
    id: navButton
    
    property string icon: ""
    property bool isSelected: false
    property alias text: buttonText.text
    signal clicked()
    
    width: parent.width
    height: 48
    
    Rectangle {
        anchors.fill: parent
        color: navButton.isSelected ? "#e0f2fe" : 
               mouseArea.containsMouse ? "#f1f5f9" : "transparent"
        radius: 8
        border.color: navButton.isSelected ? "#0ea5e9" : "transparent"
        border.width: navButton.isSelected ? 2 : 0
        
        Behavior on color {
            ColorAnimation { duration: 200 }
        }
        
        Row {
            spacing: 12
            anchors.verticalCenter: parent.verticalCenter
            anchors.left: parent.left
            anchors.leftMargin: 16
            
            Text {
                text: navButton.icon
                font.pixelSize: 18
                anchors.verticalCenter: parent.verticalCenter
            }
            
            Text {
                id: buttonText
                font.pixelSize: 14
                font.weight: navButton.isSelected ? Font.Medium : Font.Normal
                color: navButton.isSelected ? "#0ea5e9" : "#374151"
                anchors.verticalCenter: parent.verticalCenter
                
                Behavior on color {
                    ColorAnimation { duration: 200 }
                }
            }
        }
    }
    
    MouseArea {
        id: mouseArea
        anchors.fill: parent
        hoverEnabled: true
        onClicked: navButton.clicked()
        
        onPressed: navButton.scale = 0.95
        onReleased: navButton.scale = 1.0
    }
    
    // 点击效果
    Behavior on scale {
        NumberAnimation { duration: 100 }
    }
}
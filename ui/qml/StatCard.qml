import QtQuick 2.15
import QtQuick.Controls 2.15

Rectangle {
    id: statCard

    property string title: ""
    property string value: ""
    property string valueText: value  // 向后兼容
    property string subtitle: ""
    property string icon: ""
    property color cardColor: "#3b82f6"

    height: 120
    radius: 12
    color: "#ffffff"
    border.color: "#e5e7eb"
    border.width: 1

    // 悬停效果
    MouseArea {
        anchors.fill: parent
        hoverEnabled: true
        onEntered: parent.color = "#f8fafc"
        onExited: parent.color = "#ffffff"
    }

    Column {
        anchors.fill: parent
        anchors.margins: 20
        spacing: 8

        Row {
            width: parent.width
            spacing: 12

            // 图标
            Rectangle {
                width: 40
                height: 40
                radius: 8
                color: statCard.cardColor + "20" // 20% 透明度

                Text {
                    anchors.centerIn: parent
                    text: statCard.icon
                    font.pixelSize: 20
                }
            }

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
                    text: statCard.value
                    font.pixelSize: 28
                    color: "#111827"
                    font.weight: Font.Bold
                }
            }
        }

        Text {
            text: statCard.subtitle
            font.pixelSize: 12
            color: "#9ca3af"
            anchors.left: parent.left
            anchors.leftMargin: 52
        }
    }

    // 装饰性渐变
    Rectangle {
        anchors.bottom: parent.bottom
        width: parent.width
        height: 3
        radius: parent.radius
        gradient: Gradient {
            GradientStop { position: 0.0; color: statCard.cardColor }
            GradientStop { position: 1.0; color: statCard.cardColor + "60" }
        }
    }
}

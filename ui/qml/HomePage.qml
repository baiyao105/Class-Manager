import QtQuick 2.15
import QtQuick.Controls 2.15
import QtQuick.Layouts 1.15
import RinUI
import QtWebEngine

FluentPage {
    id: homePage
    title: qsTr("主页")

    // 主内容区域：加载本地 HTML 主页
    content: Item {
        anchors.fill: parent

        WebEngineView {
            anchors.fill: parent
            url: Qt.resolvedUrl("1.html")
            // 可选：启用缩放和右键菜单等
            settings.javascriptEnabled: true
            settings.pluginsEnabled: true
            settings.localStorageEnabled: true
        }
    }
}

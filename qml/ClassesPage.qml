import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI

ScrollView {
    id: classesPage

    Column {
        width: parent.width
        spacing: 24
        anchors.margins: 24

        // 页面标题和操作
        Row {
            width: parent.width

            Column {
                Text {
                    text: "班级管理"
                    font.pixelSize: 32
                    font.bold: true
                    color: "#111827"
                }

                Text {
                    text: "管理所有班级信息和设置"
                    font.pixelSize: 16
                    color: "#6b7280"
                }
            }

            Item { Layout.fillWidth: true }

            Button {
                text: "创建班级"
                highlighted: true
                icon.source: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z'/%3E%3C/svg%3E"
                anchors.verticalCenter: parent.verticalCenter
                onClicked: addClassDialog.open()
            }
        }

        // 班级统计概览
        Rectangle {
            width: parent.width
            height: 100
            color: "#ffffff"
            radius: 12
            border.color: "#e5e7eb"
            border.width: 1

            Row {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 40

                Column {
                    anchors.verticalCenter: parent.verticalCenter

                    Text {
                        text: "总班级数"
                        font.pixelSize: 14
                        color: "#6b7280"
                    }

                    Text {
                        text: controller.classes.length.toString()
                        font.pixelSize: 24
                        font.bold: true
                        color: "#2563eb"
                    }
                }

                Column {
                    anchors.verticalCenter: parent.verticalCenter

                    Text {
                        text: "总学生数"
                        font.pixelSize: 14
                        color: "#6b7280"
                    }

                    Text {
                        text: controller.classes.reduce((sum, cls) => sum + cls.studentCount, 0).toString()
                        font.pixelSize: 24
                        font.bold: true
                        color: "#059669"
                    }
                }

                Column {
                    anchors.verticalCenter: parent.verticalCenter

                    Text {
                        text: "平均班级人数"
                        font.pixelSize: 14
                        color: "#6b7280"
                    }

                    Text {
                        text: controller.classes.length > 0 ?
                              (controller.classes.reduce((sum, cls) => sum + cls.studentCount, 0) / controller.classes.length).toFixed(1) : "0"
                        font.pixelSize: 24
                        font.bold: true
                        color: "#f59e0b"
                    }
                }
            }
        }

        // 班级卡片网格
        GridLayout {
            width: parent.width
            columns: 3
            columnSpacing: 16
            rowSpacing: 16

            Repeater {
                model: controller.classes

                delegate: Rectangle {
                    Layout.preferredWidth: (parent.width - 32) / 3
                    Layout.preferredHeight: 280
                    color: "#ffffff"
                    radius: 12
                    border.color: "#e5e7eb"
                    border.width: 1

                    // 悬停效果
                    MouseArea {
                        anchors.fill: parent
                        hoverEnabled: true

                        onEntered: parent.border.color = "#2563eb"
                        onExited: parent.border.color = "#e5e7eb"
                    }

                    Column {
                        anchors.fill: parent
                        anchors.margins: 20
                        spacing: 16

                        // 班级头部信息
                        Row {
                            width: parent.width

                            Column {
                                width: parent.width - 60

                                Text {
                                    text: modelData.name
                                    font.pixelSize: 20
                                    font.bold: true
                                    color: "#111827"
                                    elide: Text.ElideRight
                                    width: parent.width
                                }

                                Text {
                                    text: "班主任：" + modelData.teacherName
                                    font.pixelSize: 14
                                    color: "#6b7280"
                                    elide: Text.ElideRight
                                    width: parent.width
                                }
                            }

                            Rectangle {
                                width: 40
                                height: 40
                                radius: 20
                                color: modelData.isActive ? "#dcfce7" : "#fef3c7"

                                Text {
                                    text: modelData.isActive ? "✓" : "⏸"
                                    anchors.centerIn: parent
                                    font.pixelSize: 18
                                    color: modelData.isActive ? "#166534" : "#92400e"
                                }
                            }
                        }

                        // 分隔线
                        Rectangle {
                            width: parent.width
                            height: 1
                            color: "#e5e7eb"
                        }

                        // 统计信息
                        Column {
                            width: parent.width
                            spacing: 12

                            Row {
                                width: parent.width

                                Text {
                                    text: "学生数量"
                                    font.pixelSize: 14
                                    color: "#6b7280"
                                    width: parent.width / 2
                                }

                                Text {
                                    text: modelData.studentCount + "人"
                                    font.pixelSize: 14
                                    font.bold: true
                                    color: "#111827"
                                    horizontalAlignment: Text.AlignRight
                                    width: parent.width / 2
                                }
                            }

                            Row {
                                width: parent.width

                                Text {
                                    text: "平均分数"
                                    font.pixelSize: 14
                                    color: "#6b7280"
                                    width: parent.width / 2
                                }

                                Text {
                                    text: modelData.averageScore.toFixed(1) + "分"
                                    font.pixelSize: 14
                                    font.bold: true
                                    color: "#059669"
                                    horizontalAlignment: Text.AlignRight
                                    width: parent.width / 2
                                }
                            }

                            Row {
                                width: parent.width

                                Text {
                                    text: "班级排名"
                                    font.pixelSize: 14
                                    color: "#6b7280"
                                    width: parent.width / 2
                                }

                                Text {
                                    text: "第" + (index + 1) + "名"
                                    font.pixelSize: 14
                                    font.bold: true
                                    color: index === 0 ? "#fbbf24" :
                                           index === 1 ? "#9ca3af" :
                                           index === 2 ? "#cd7f32" : "#6b7280"
                                    horizontalAlignment: Text.AlignRight
                                    width: parent.width / 2
                                }
                            }
                        }

                        // 操作按钮
                        Row {
                            width: parent.width
                            spacing: 8

                            Button {
                                text: "查看详情"
                                flat: true
                                width: (parent.width - 8) / 2
                                onClicked: {
                                    console.log("查看班级详情:", modelData.name)
                                }
                            }

                            Button {
                                text: "管理学生"
                                highlighted: true
                                width: (parent.width - 8) / 2
                                onClicked: {
                                    console.log("管理班级学生:", modelData.name)
                                }
                            }
                        }

                        // 更多操作
                        Row {
                            width: parent.width
                            spacing: 8

                            Button {
                                text: "编辑"
                                flat: true
                                width: (parent.width - 16) / 3
                                font.pixelSize: 12
                                onClicked: {
                                    editClassDialog.classId = modelData.id
                                    editClassDialog.className = modelData.name
                                    editClassDialog.teacherName = modelData.teacherName
                                    editClassDialog.open()
                                }
                            }

                            Button {
                                text: modelData.isActive ? "停用" : "启用"
                                flat: true
                                width: (parent.width - 16) / 3
                                font.pixelSize: 12
                                palette.buttonText: modelData.isActive ? "#dc2626" : "#059669"
                                onClicked: {
                                    console.log(modelData.isActive ? "停用班级:" : "启用班级:", modelData.name)
                                }
                            }

                            Button {
                                text: "删除"
                                flat: true
                                width: (parent.width - 16) / 3
                                font.pixelSize: 12
                                palette.buttonText: "#dc2626"
                                onClicked: {
                                    deleteClassDialog.classId = modelData.id
                                    deleteClassDialog.className = modelData.name
                                    deleteClassDialog.open()
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // 添加班级对话框
    Dialog {
        id: addClassDialog
        title: "创建班级"
        modal: true
        anchors.centerIn: parent
        width: 400
        height: 300

        Column {
            anchors.fill: parent
            spacing: 16

            TextField {
                id: classNameField
                width: parent.width
                placeholderText: "班级名称"

                background: Rectangle {
                    color: "#f9fafb"
                    radius: 8
                    border.color: classNameField.activeFocus ? "#2563eb" : "#d1d5db"
                    border.width: 1
                }
            }

            TextField {
                id: teacherNameField
                width: parent.width
                placeholderText: "班主任姓名"

                background: Rectangle {
                    color: "#f9fafb"
                    radius: 8
                    border.color: teacherNameField.activeFocus ? "#2563eb" : "#d1d5db"
                    border.width: 1
                }
            }

            TextField {
                id: teacherContactField
                width: parent.width
                placeholderText: "班主任联系方式 (可选)"

                background: Rectangle {
                    color: "#f9fafb"
                    radius: 8
                    border.color: teacherContactField.activeFocus ? "#2563eb" : "#d1d5db"
                    border.width: 1
                }
            }

            ComboBox {
                id: classTypeCombo
                width: parent.width
                model: ["普通班", "荣誉班", "特殊班"]
                currentIndex: 0
            }
        }

        standardButtons: Dialog.Ok | Dialog.Cancel

        onAccepted: {
            if (classNameField.text && teacherNameField.text) {
                controller.addClass(classNameField.text, teacherNameField.text)
                classNameField.clear()
                teacherNameField.clear()
                teacherContactField.clear()
                classTypeCombo.currentIndex = 0
            }
        }
    }

    // 编辑班级对话框
    Dialog {
        id: editClassDialog
        title: "编辑班级"
        modal: true
        anchors.centerIn: parent
        width: 400
        height: 300

        property int classId: 0
        property string className: ""
        property string teacherName: ""

        Column {
            anchors.fill: parent
            spacing: 16

            TextField {
                id: editClassNameField
                width: parent.width
                text: editClassDialog.className
                placeholderText: "班级名称"

                background: Rectangle {
                    color: "#f9fafb"
                    radius: 8
                    border.color: editClassNameField.activeFocus ? "#2563eb" : "#d1d5db"
                    border.width: 1
                }
            }

            TextField {
                id: editTeacherNameField
                width: parent.width
                text: editClassDialog.teacherName
                placeholderText: "班主任姓名"

                background: Rectangle {
                    color: "#f9fafb"
                    radius: 8
                    border.color: editTeacherNameField.activeFocus ? "#2563eb" : "#d1d5db"
                    border.width: 1
                }
            }
        }

        standardButtons: Dialog.Ok | Dialog.Cancel

        onAccepted: {
            if (editClassNameField.text && editTeacherNameField.text) {
                console.log("更新班级:", editClassDialog.classId, editClassNameField.text, editTeacherNameField.text)
                // 这里应该调用controller的更新方法
            }
        }
    }

    // 删除班级确认对话框
    Dialog {
        id: deleteClassDialog
        title: "确认删除"
        modal: true
        anchors.centerIn: parent
        width: 350
        height: 200

        property int classId: 0
        property string className: ""

        Text {
            anchors.centerIn: parent
            text: "确定要删除班级 \"" + deleteClassDialog.className + "\" 吗？\n此操作将同时删除班级内的所有学生数据, 且不可撤销。"
            horizontalAlignment: Text.AlignHCenter
            color: "#374151"
            wrapMode: Text.WordWrap
        }

        standardButtons: Dialog.Yes | Dialog.No

        onAccepted: {
            controller.deleteClass(deleteClassDialog.classId)
        }
    }
}

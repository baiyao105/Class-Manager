import QtQuick
import QtQuick.Controls
import QtQuick.Layouts
import RinUI

ScrollView {
    id: studentsPage

    Column {
        width: parent.width
        spacing: 24
        anchors.margins: 24

        // 页面标题和操作
        Row {
            width: parent.width

            Column {
                Text {
                    text: "学生管理"
                    font.pixelSize: 32
                    font.bold: true
                    color: "#111827"
                }

                Text {
                    text: "管理所有学生信息和成绩"
                    font.pixelSize: 16
                    color: "#6b7280"
                }
            }

            Item { Layout.fillWidth: true }

            Button {
                text: "添加学生"
                highlighted: true
                icon.source: "data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 24 24' fill='white'%3E%3Cpath d='M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z'/%3E%3C/svg%3E"
                anchors.verticalCenter: parent.verticalCenter
                onClicked: addStudentDialog.open()
            }
        }

        // 搜索和筛选
        Rectangle {
            width: parent.width
            height: 80
            color: "#ffffff"
            radius: 12
            border.color: "#e5e7eb"
            border.width: 1

            Row {
                anchors.fill: parent
                anchors.margins: 20
                spacing: 16

                TextField {
                    id: searchField
                    width: 300
                    placeholderText: "搜索学生姓名或学号..."
                    anchors.verticalCenter: parent.verticalCenter

                    background: Rectangle {
                        color: "#f9fafb"
                        radius: 8
                        border.color: searchField.activeFocus ? "#2563eb" : "#d1d5db"
                        border.width: 1
                    }
                }

                ComboBox {
                    id: classFilter
                    width: 150
                    model: ["全部班级"].concat(controller.classes.map(c => c.name))
                    anchors.verticalCenter: parent.verticalCenter
                }

                ComboBox {
                    id: statusFilter
                    width: 120
                    model: ["全部状态", "活跃", "非活跃"]
                    anchors.verticalCenter: parent.verticalCenter
                }

                Button {
                    text: "搜索"
                    anchors.verticalCenter: parent.verticalCenter
                    onClicked: {
                        // 实现搜索逻辑
                        console.log("搜索:", searchField.text)
                    }
                }
            }
        }

        // 学生列表
        Rectangle {
            width: parent.width
            height: 500
            color: "#ffffff"
            radius: 12
            border.color: "#e5e7eb"
            border.width: 1

            Column {
                anchors.fill: parent

                // 表头
                Rectangle {
                    width: parent.width
                    height: 50
                    color: "#f9fafb"
                    radius: 12

                    Row {
                        anchors.fill: parent
                        anchors.margins: 16

                        Text {
                            text: "姓名"
                            width: 100
                            font.bold: true
                            color: "#374151"
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Text {
                            text: "学号"
                            width: 100
                            font.bold: true
                            color: "#374151"
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Text {
                            text: "班级"
                            width: 120
                            font.bold: true
                            color: "#374151"
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Text {
                            text: "当前分数"
                            width: 100
                            font.bold: true
                            color: "#374151"
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Text {
                            text: "排名"
                            width: 80
                            font.bold: true
                            color: "#374151"
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Text {
                            text: "状态"
                            width: 80
                            font.bold: true
                            color: "#374151"
                            anchors.verticalCenter: parent.verticalCenter
                        }

                        Text {
                            text: "操作"
                            width: 150
                            font.bold: true
                            color: "#374151"
                            anchors.verticalCenter: parent.verticalCenter
                        }
                    }
                }

                // 学生列表
                ListView {
                    width: parent.width
                    height: parent.height - 50
                    model: controller.students

                    delegate: Rectangle {
                        width: parent.width
                        height: 60
                        color: index % 2 === 0 ? "#ffffff" : "#f9fafb"

                        MouseArea {
                            anchors.fill: parent
                            hoverEnabled: true

                            onEntered: parent.color = "#e0f2fe"
                            onExited: parent.color = index % 2 === 0 ? "#ffffff" : "#f9fafb"
                        }

                        Row {
                            anchors.fill: parent
                            anchors.margins: 16

                            Text {
                                text: modelData.name
                                width: 100
                                color: "#111827"
                                font.weight: Font.Medium
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Text {
                                text: modelData.studentNumber
                                width: 100
                                color: "#6b7280"
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Text {
                                text: modelData.className
                                width: 120
                                color: "#6b7280"
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Text {
                                text: modelData.currentScore.toFixed(1)
                                width: 100
                                color: "#059669"
                                font.bold: true
                                anchors.verticalCenter: parent.verticalCenter
                            }

                            Rectangle {
                                width: 30
                                height: 20
                                radius: 10
                                color: modelData.rank <= 3 ? "#fbbf24" : "#e5e7eb"
                                anchors.verticalCenter: parent.verticalCenter

                                Text {
                                    text: modelData.rank.toString()
                                    anchors.centerIn: parent
                                    font.pixelSize: 12
                                    font.bold: true
                                    color: modelData.rank <= 3 ? "white" : "#374151"
                                }
                            }

                            Rectangle {
                                width: 60
                                height: 24
                                radius: 12
                                color: modelData.status === "活跃" ? "#dcfce7" : "#fef3c7"
                                anchors.verticalCenter: parent.verticalCenter

                                Text {
                                    text: modelData.status
                                    anchors.centerIn: parent
                                    font.pixelSize: 11
                                    color: modelData.status === "活跃" ? "#166534" : "#92400e"
                                }
                            }

                            Row {
                                width: 150
                                spacing: 8
                                anchors.verticalCenter: parent.verticalCenter

                                Button {
                                    text: "编辑"
                                    flat: true
                                    font.pixelSize: 12
                                    onClicked: {
                                        console.log("编辑学生:", modelData.name)
                                    }
                                }

                                Button {
                                    text: "删除"
                                    flat: true
                                    font.pixelSize: 12
                                    palette.buttonText: "#dc2626"
                                    onClicked: {
                                        deleteConfirmDialog.studentId = modelData.id
                                        deleteConfirmDialog.studentName = modelData.name
                                        deleteConfirmDialog.open()
                                    }
                                }
                            }
                        }
                    }
                }
            }
        }
    }

    // 添加学生对话框
    Dialog {
        id: addStudentDialog
        title: "添加学生"
        modal: true
        anchors.centerIn: parent
        width: 400
        height: 350

        Column {
            anchors.fill: parent
            spacing: 16

            TextField {
                id: studentNameField
                width: parent.width
                placeholderText: "学生姓名"

                background: Rectangle {
                    color: "#f9fafb"
                    radius: 8
                    border.color: studentNameField.activeFocus ? "#2563eb" : "#d1d5db"
                    border.width: 1
                }
            }

            TextField {
                id: studentNumberField
                width: parent.width
                placeholderText: "学号"

                background: Rectangle {
                    color: "#f9fafb"
                    radius: 8
                    border.color: studentNumberField.activeFocus ? "#2563eb" : "#d1d5db"
                    border.width: 1
                }
            }

            ComboBox {
                id: classComboBox
                width: parent.width
                model: controller.classes.map(c => c.name)
                displayText: currentIndex >= 0 ? currentText : "选择班级"
            }

            TextField {
                id: initialScoreField
                width: parent.width
                placeholderText: "初始分数 (可选, 默认0)"
                validator: DoubleValidator { bottom: -999; top: 999 }

                background: Rectangle {
                    color: "#f9fafb"
                    radius: 8
                    border.color: initialScoreField.activeFocus ? "#2563eb" : "#d1d5db"
                    border.width: 1
                }
            }
        }

        standardButtons: Dialog.Ok | Dialog.Cancel

        onAccepted: {
            if (studentNameField.text && studentNumberField.text && classComboBox.currentIndex >= 0) {
                controller.addStudent(
                    studentNameField.text,
                    studentNumberField.text,
                    controller.classes[classComboBox.currentIndex].name
                )
                studentNameField.clear()
                studentNumberField.clear()
                initialScoreField.clear()
                classComboBox.currentIndex = -1
            }
        }
    }

    // 删除确认对话框
    Dialog {
        id: deleteConfirmDialog
        title: "确认删除"
        modal: true
        anchors.centerIn: parent
        width: 350
        height: 200

        property int studentId: 0
        property string studentName: ""

        Text {
            anchors.centerIn: parent
            text: "确定要删除学生 \"" + deleteConfirmDialog.studentName + "\" 吗？\n此操作不可撤销。"
            horizontalAlignment: Text.AlignHCenter
            color: "#374151"
        }

        standardButtons: Dialog.Yes | Dialog.No

        onAccepted: {
            controller.deleteStudent(deleteConfirmDialog.studentId)
        }
    }
}

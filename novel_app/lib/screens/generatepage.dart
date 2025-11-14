import 'package:flutter/material.dart';

class GenerateNovelPage extends StatefulWidget {
  const GenerateNovelPage({super.key});

  // This widget is the home page of your application. It is stateful, meaning
  // that it has a State object (defined below) that contains fields that affect
  // how it looks.

  // This class is the configuration for the state. It holds the values (in this
  // case the title) provided by the parent (in this case the App widget) and
  // used by the build method of the State. Fields in a Widget subclass are
  // always marked "final".

  @override
  State<GenerateNovelPage> createState() => _GenerateNovelPageState();
}

class _GenerateNovelPageState extends State<GenerateNovelPage> {
  String isSelectedValue = 'あ';
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: Text("小説設定"),
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text("生成する小説の設定"),
            DropdownButton(
              items: const [
                DropdownMenuItem(value: 'あ', child: Text('あ')),
                DropdownMenuItem(value: 'い', child: Text('い')),
                DropdownMenuItem(value: 'う', child: Text('う')),
                DropdownMenuItem(value: 'え', child: Text('え')),
                DropdownMenuItem(value: 'お', child: Text('お')),
              ],
              value: isSelectedValue,
              onChanged: (String? value) {
                setState(() {
                  isSelectedValue = value!;
                });
              },
            ),
          ],
        ),
      ),
    );
  }
}

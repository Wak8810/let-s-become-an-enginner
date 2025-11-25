import 'package:flutter/material.dart';
import '../utils/api_service.dart';

class TestApiPage extends StatefulWidget {
  const TestApiPage({super.key});

  @override
  State<TestApiPage> createState() => _TestApiPageState();
}

class _TestApiPageState extends State<TestApiPage> {
  String apiResult = "";

  @override
  void initState() {
    super.initState();
    _loadApi();
  }

  Future<void> _loadApi() async {
    final result = await fetchApiData();
    setState(() {
      apiResult = result;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text("APIテストページ")),
      body: Center(
        child: Text(apiResult.isEmpty ? "読み込み中..." : apiResult),
      ),
    );
  }
}

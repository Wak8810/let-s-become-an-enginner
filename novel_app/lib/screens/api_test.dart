import 'package:flutter/material.dart';
import '../utils/api_service.dart';
import 'package:provider/provider.dart';


class TestApiPage extends StatefulWidget {
  const TestApiPage({super.key});

  @override
  State<TestApiPage> createState() => _TestApiPageState();
}

class _TestApiPageState extends State<TestApiPage> {
  String apiResult = "";
  late String _userId;

  @override
  void initState() {
    super.initState();
    _loadApi();
  }

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    _userId = Provider.of<String>(context);
  }

  Future<void> _loadApi() async {
    final result = await fetchApiData(_userId);
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

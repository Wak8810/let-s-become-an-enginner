import 'package:flutter/material.dart';
import '../../utils/get_rest_novel.dart';
import 'package:provider/provider.dart';

class NovelViewScreen extends StatefulWidget {
  const NovelViewScreen({
    super.key,
    required this.title,
    required this.text,
    required this.novelId,
    required this.finalChapterIndex,
    required this.totalChapterNumber,
  });

  final String title;
  final String text;
  final String novelId;
  final int finalChapterIndex;
  final int totalChapterNumber;

  @override
  State<NovelViewScreen> createState() => _NovelViewScreenState();
}

class _NovelViewScreenState extends State<NovelViewScreen> {
  bool isLoading = false;
  String fullText = "";
  late String _userId;
  bool _isInitialized = false;
  int currentIndex = 1;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    if (!_isInitialized) {
      _userId = Provider.of<String>(context);
      _isInitialized = true;
    }
  }

  @override
  void initState() {
    super.initState();
    fullText = widget.text;
    currentIndex = widget.finalChapterIndex;
  }

  Future<void> _loadMore() async {
    if (isLoading) return; // 連打防止

    setState(() {
      isLoading = true; // ボタンを消してクルクル開始
    });

    try {
      final (newText, newIndex) = await fetchRestNovel(
        currentIndex,
        widget.novelId,
        _userId,
      );

      setState(() {
        fullText += '\n' + newText; // 文章を追加
        currentIndex = newIndex;
      });
    } finally {
      setState(() {
        isLoading = false; // ローディング終了
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
        title: const Text('閲覧ページ'),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(
              widget.title,
              style: Theme.of(
                context,
              ).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Expanded(
              child: SingleChildScrollView(
                padding: const EdgeInsets.all(12),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      fullText,
                      style: const TextStyle(fontSize: 16, height: 1.6),
                    ),
                    const SizedBox(height: 20),

                    isLoading
                        ? const Center(child: CircularProgressIndicator())
                        : (currentIndex >=
                                  widget.totalChapterNumber
                              ? const SizedBox() // ← 何も表示しない
                              : ElevatedButton(
                                  onPressed: _loadMore,
                                  child: const Text("続きを読み込む"),
                                )),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

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
    if (isLoading) return;

    setState(() => isLoading = true);

    try {
      final (newText, newIndex) = await fetchRestNovel(
        currentIndex,
        widget.novelId,
        _userId,
      );

      setState(() {
        if (newText.isNotEmpty) {
          fullText += "\n$newText";
        }
        currentIndex = newIndex;
      });
    } finally {
      setState(() => isLoading = false);
    }
  }

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Scaffold(
      backgroundColor: Colors.white,
      appBar: AppBar(
        elevation: 0,
        backgroundColor: Colors.white,
        foregroundColor: Colors.black87,
        title: Text(
          '閲覧ページ',
          style: theme.textTheme.titleMedium?.copyWith(
            fontWeight: FontWeight.w600,
          ),
        ),
      ),
      body: Column(
        children: [
          // タイトル
          Padding(
            padding: const EdgeInsets.fromLTRB(18, 10, 18, 8),
            child: Text(
              widget.title,
              style: theme.textTheme.headlineSmall?.copyWith(
                fontWeight: FontWeight.bold,
                height: 1.3,
              ),
            ),
          ),

          // 本文
          Expanded(
            child: SingleChildScrollView(
              padding: const EdgeInsets.fromLTRB(20, 12, 20, 80),
              child: Text(
                fullText,
                style: const TextStyle(
                  fontSize: 18,
                  height: 1.8,
                  fontWeight: FontWeight.w400,
                  color: Colors.black87,
                ),
              ),
            ),
          ),
        ],
      ),

      // 下部にボタン固定（iPhoneアプリっぽい）
      bottomNavigationBar: currentIndex >= widget.totalChapterNumber
          ? const SizedBox(height: 0)
          : Container(
              padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
              decoration: const BoxDecoration(
                color: Colors.white,
                border: Border(top: BorderSide(color: Colors.black12)),
              ),
              child: SizedBox(
                height: 48,
                width: double.infinity,
                child: ElevatedButton(
                  onPressed: isLoading ? null : _loadMore,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.black,
                    foregroundColor: Colors.white,
                    shape: RoundedRectangleBorder(
                      borderRadius: BorderRadius.circular(12),
                    ),
                    elevation: 0,
                  ),
                  child: isLoading
                      ? const CircularProgressIndicator(
                          strokeWidth: 2,
                          valueColor: AlwaysStoppedAnimation(Colors.white),
                        )
                      : const Text("続きを読み込む", style: TextStyle(fontSize: 16)),
                ),
              ),
            ),
    );
  }
}

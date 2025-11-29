import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:novel_app/main.dart';
import 'package:novel_app/utils/get_user_all_novels.dart';
import 'package:novel_app/screens/novel_list/widgets/novel_card.dart';
import 'package:novel_app/models/novel.dart';
import 'package:novel_app/widgets/generate_novel_screen_button.dart';

class NovelListScreen extends StatefulWidget {
  const NovelListScreen({super.key, required this.userId});
  final String userId;

  @override
  State<NovelListScreen> createState() => _NovelListScreenState();
}

class _NovelListScreenState extends State<NovelListScreen> {
  Future<List<Novel>>? _novels;

  @override
  void initState() {
    super.initState();
    _novels = GetUserAllNovels.fetchNovels(widget.userId);
  }

  Future<void> _refreshNovels() async {
    setState(() {
      _novels = GetUserAllNovels.fetchNovels(widget.userId);
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('小説一覧'),
        bottom: PreferredSize(
          preferredSize: const Size.fromHeight(kToolbarHeight / 2),
          child: Align(
            alignment: Alignment.centerRight,
            child: IconButton(
              icon: const Icon(Icons.refresh),
              onPressed: _refreshNovels,
            ),
          ),
        ),
      ),
      body: FutureBuilder<List<Novel>>(
        future: _novels,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          } else if (snapshot.hasError) {
            return Center(child: Text('Error: ${snapshot.error}'));
          } else if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('小説がありません。'));
          } else {
            final novels = snapshot.data!;
            novels.sort((a, b) => b.createdAt.compareTo(a.createdAt));
            return ListView.builder(
              itemCount: novels.length,
              itemBuilder: (context, index) {
                return NovelCard(novel: novels[index]);
              },
            );
          }
        },
      ),
      floatingActionButton: const GenerateNovelScreen(),
    );
  }
}

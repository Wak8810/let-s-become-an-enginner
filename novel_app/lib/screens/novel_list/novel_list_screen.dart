import 'package:flutter/material.dart';
import 'package:novel_app/utils/get_user_all_novels.dart';
import 'package:novel_app/screens/novel_list/widgets/novel_card.dart';
import 'package:novel_app/models/novel.dart';
import 'package:novel_app/widgets/generate_novel_screen_button.dart';
import 'package:novel_app/main.dart';
import 'package:provider/provider.dart';

class NovelListScreen extends StatefulWidget {
  const NovelListScreen({super.key});

  @override
  State<NovelListScreen> createState() => _NovelListScreenState();
}

class _NovelListScreenState extends State<NovelListScreen> with RouteAware {
  List<Novel>? _novels;
  bool _isLoading = true;
  late String _userId;
  bool _isInitialized = false;

  @override
  void didChangeDependencies() {
    super.didChangeDependencies();
    // 初期化とデータ取得が一度だけ行われるようにする
    if (!_isInitialized) {
      _userId = Provider.of<String>(context);
      // routeObserverをサブスクして，このページになったのを見る
      routeObserver.subscribe(this, ModalRoute.of(context)! as PageRoute);
      _fetchInitialNovels();
      _isInitialized = true;
    }
  }

  // 小説の初期リストを取得し、ローディング状態を設定
  Future<void> _fetchInitialNovels() async {
    final novels = await GetUserAllNovels.fetchNovels(_userId);
    if (mounted) {
      setState(() {
        _novels = novels;
        _isLoading = false;
      });
    }
  }

  // こいつが完全に閉じたら，サブスクを解除
  @override
  void dispose() {
    routeObserver.unsubscribe(this);
    super.dispose();
  }

  /// ユーザーが戻るでこの画面に来た時実行
  @override
  void didPopNext() {
    _refreshNovels();
  }

  /// APIから小説の新しいリストを取得
  Future<void> _refreshNovels() async {
    final novels = await GetUserAllNovels.fetchNovels(_userId);
    if (mounted) {
      setState(() {
        _novels = novels; // 新しいデータで更新
      });
    }
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
      body: _isLoading
          ? const Center(child: CircularProgressIndicator()) // ローディングのくるくる
          : _novels == null || _novels!.isEmpty
              ? const Center(child: Text('小説がありません。'))
              : ListView.builder(
                  itemCount: _novels!.length,
                  itemBuilder: (context, index) {
                    // 作成日で小説をソート（新しいものが先頭）。
                    _novels!.sort((a, b) => b.createdAt.compareTo(a.createdAt));
                    return NovelCard(novel: _novels![index]);
                  },
                ),
      floatingActionButton: const GenerateNovelScreen(),
    );
  }
}

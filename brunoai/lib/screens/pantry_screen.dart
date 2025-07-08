import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../models/pantry_item.dart';
import '../providers/bruno_provider.dart';
import '../theme/app_colors.dart';

class PantryScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Pantry Inventory'),
      ),
      body: Consumer<BrunoProvider>(
        builder: (context, provider, child) => ListView.builder(
          itemCount: provider.pantryList.length,
          itemBuilder: (context, index) {
            final item = provider.pantryList[index];
            return ListTile(
              title: Text(item.name),
              subtitle: Text('Expires on: ${item.expirationDate.toLocal()}'),
              trailing: Text('${item.quantity} left'),
              onTap: () {
                // Navigate to edit or details screen
              },
            );
          },
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {
          // Navigate to add new pantry item screen
        },
        child: Icon(Icons.add),
      ),
    );
  }
}


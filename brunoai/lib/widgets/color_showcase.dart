import 'package:flutter/material.dart';
import '../theme/app_colors.dart';

/// Widget to showcase the new unified color system
/// This helps developers see all available colors in the app
class ColorShowcase extends StatelessWidget {
  const ColorShowcase({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Bruno AI - Unified Colors'),
        centerTitle: true,
      ),
      body: ListView(
        padding: const EdgeInsets.all(20),
        children: [
          _buildSectionHeader('Primary Brand Colors (Bruno Brown)'),
          _buildColorGrid([
            _ColorItem('Primary', AppColors.primary, '#8B4513'),
            _ColorItem('Primary Light', AppColors.primaryLight, '#D2691E'),
            _ColorItem('Primary Dark', AppColors.primaryDark, '#6B3410'),
          ]),
          
          const SizedBox(height: 32),
          _buildSectionHeader('Interactive Elements (Indigo)'),
          _buildColorGrid([
            _ColorItem('Interactive Blue', AppColors.interactiveBlue, '#6366F1'),
            _ColorItem('Interactive Light', AppColors.interactiveBlueLight, '#8B5CF6'),
            _ColorItem('Interactive Dark', AppColors.interactiveBlueDark, '#4F46E5'),
          ]),
          
          const SizedBox(height: 32),
          _buildSectionHeader('System Colors'),
          _buildColorGrid([
            _ColorItem('Success', AppColors.success, '#10B981'),
            _ColorItem('Warning', AppColors.warning, '#F59E0B'),
            _ColorItem('Error', AppColors.error, '#EF4444'),
            _ColorItem('Instacart Green', AppColors.instacartGreen, '#43B02A'),
          ]),
          
          const SizedBox(height: 32),
          _buildSectionHeader('Neutral Scale'),
          _buildColorGrid([
            _ColorItem('White', AppColors.white, '#FFFFFF'),
            _ColorItem('Gray 50', AppColors.gray50, '#FAFAFA'),
            _ColorItem('Gray 100', AppColors.gray100, '#F5F5F5'),
            _ColorItem('Gray 200', AppColors.gray200, '#E5E5E5'),
            _ColorItem('Gray 300', AppColors.gray300, '#D4D4D4'),
            _ColorItem('Gray 400', AppColors.gray400, '#A3A3A3'),
            _ColorItem('Gray 500', AppColors.gray500, '#737373'),
            _ColorItem('Gray 600', AppColors.gray600, '#525252'),
            _ColorItem('Gray 700', AppColors.gray700, '#404040'),
            _ColorItem('Gray 800', AppColors.gray800, '#262626'),
            _ColorItem('Gray 900', AppColors.gray900, '#171717'),
          ]),
          
          const SizedBox(height: 32),
          _buildSectionHeader('Modern Buttons'),
          _buildButtonShowcase(),
          
          const SizedBox(height: 32),
          _buildSectionHeader('Typography Examples'),
          _buildTypographyShowcase(),
          
          const SizedBox(height: 32),
          _buildSectionHeader('Cards & Surfaces'),
          _buildCardShowcase(),
        ],
      ),
    );
  }
  
  Widget _buildSectionHeader(String title) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Text(
        title,
        style: const TextStyle(
          fontSize: 24,
          fontWeight: FontWeight.w700,
          color: AppColors.gray900,
        ),
      ),
    );
  }
  
  Widget _buildColorGrid(List<_ColorItem> colors) {
    return GridView.builder(
      shrinkWrap: true,
      physics: const NeverScrollableScrollPhysics(),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 3,
        childAspectRatio: 1.2,
        crossAxisSpacing: 12,
        mainAxisSpacing: 12,
      ),
      itemCount: colors.length,
      itemBuilder: (context, index) {
        final color = colors[index];
        return Container(
          decoration: BoxDecoration(
            color: color.color,
            borderRadius: BorderRadius.circular(16),
            border: Border.all(
              color: AppColors.gray200,
              width: 1,
            ),
            boxShadow: [
              BoxShadow(
                color: AppColors.shadowLight,
                blurRadius: 8,
                offset: const Offset(0, 4),
              ),
            ],
          ),
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text(
                color.name,
                style: TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: _getContrastColor(color.color),
                ),
                textAlign: TextAlign.center,
              ),
              const SizedBox(height: 4),
              Text(
                color.hex,
                style: TextStyle(
                  fontSize: 10,
                  fontWeight: FontWeight.w400,
                  color: _getContrastColor(color.color).withOpacity(0.8),
                ),
                textAlign: TextAlign.center,
              ),
            ],
          ),
        );
      },
    );
  }
  
  Widget _buildButtonShowcase() {
    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child: ElevatedButton(
                onPressed: () {},
                child: const Text('Primary Button'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: OutlinedButton(
                onPressed: () {},
                child: const Text('Outlined Button'),
              ),
            ),
          ],
        ),
        const SizedBox(height: 12),
        Row(
          children: [
            Expanded(
              child: TextButton(
                onPressed: () {},
                child: const Text('Text Button'),
              ),
            ),
            const SizedBox(width: 12),
            Expanded(
              child: ElevatedButton.icon(
                onPressed: () {},
                icon: const Icon(Icons.star),
                label: const Text('Icon Button'),
              ),
            ),
          ],
        ),
      ],
    );
  }
  
  Widget _buildTypographyShowcase() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Display Large',
          style: Theme.of(context).textTheme.displayLarge,
        ),
        const SizedBox(height: 8),
        Text(
          'Headline Large',
          style: Theme.of(context).textTheme.headlineLarge,
        ),
        const SizedBox(height: 8),
        Text(
          'Title Large',
          style: Theme.of(context).textTheme.titleLarge,
        ),
        const SizedBox(height: 8),
        Text(
          'Body Large - This is a sample of body text that shows how the typography system works.',
          style: Theme.of(context).textTheme.bodyLarge,
        ),
        const SizedBox(height: 8),
        Text(
          'Body Medium - Smaller body text for secondary content.',
          style: Theme.of(context).textTheme.bodyMedium,
        ),
      ],
    );
  }
  
  Widget _buildCardShowcase() {
    return Row(
      children: [
        Expanded(
          child: Card(
            child: Padding(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text(
                    'Modern Card',
                    style: TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'This card uses the new design system with modern colors and typography.',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                ],
              ),
            ),
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: AppColors.primary.withOpacity(0.1),
              borderRadius: BorderRadius.circular(24),
              border: Border.all(
                color: AppColors.primary.withOpacity(0.2),
                width: 1,
              ),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Accent Container',
                  style: TextStyle(
                    fontSize: 18,
                    fontWeight: FontWeight.w600,
                    color: AppColors.primary,
                  ),
                ),
                const SizedBox(height: 8),
                Text(
                  'This container showcases the primary color system.',
                  style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                    color: AppColors.primaryDark,
                  ),
                ),
              ],
            ),
          ),
        ),
      ],
    );
  }
  
  Color _getContrastColor(Color backgroundColor) {
    // Calculate the relative luminance
    final brightness = backgroundColor.computeLuminance();
    return brightness > 0.5 ? AppColors.gray900 : AppColors.white;
  }
}

class _ColorItem {
  final String name;
  final Color color;
  final String hex;
  
  const _ColorItem(this.name, this.color, this.hex);
}

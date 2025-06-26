import 'package:flutter/material.dart';
import 'dart:math' as math;
import 'dart:ui';

class AnimatedBackground extends StatefulWidget {
  final Widget child;
  final List<Color>? colors;
  final Duration duration;
  final bool enableParticles;
  
  const AnimatedBackground({
    super.key,
    required this.child,
    this.colors,
    this.duration = const Duration(seconds: 20),
    this.enableParticles = true,
  });

  @override
  State<AnimatedBackground> createState() => _AnimatedBackgroundState();
}

class _AnimatedBackgroundState extends State<AnimatedBackground>
    with TickerProviderStateMixin {
  late AnimationController _gradientController;
  late AnimationController _particleController;
  late Animation<double> _gradientAnimation;
  late Animation<double> _particleAnimation;
  
  final List<Particle> _particles = [];
  final int _particleCount = 15;

  @override
  void initState() {
    super.initState();
    
    _gradientController = AnimationController(
      duration: widget.duration,
      vsync: this,
    );
    
    _particleController = AnimationController(
      duration: const Duration(seconds: 30),
      vsync: this,
    );
    
    _gradientAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _gradientController,
      curve: Curves.easeInOut,
    ));
    
    _particleAnimation = Tween<double>(
      begin: 0.0,
      end: 1.0,
    ).animate(CurvedAnimation(
      parent: _particleController,
      curve: Curves.linear,
    ));
    
    _gradientController.repeat(reverse: true);
    _particleController.repeat();
    
    if (widget.enableParticles) {
      _initializeParticles();
    }
  }

  @override
  void dispose() {
    _gradientController.dispose();
    _particleController.dispose();
    super.dispose();
  }

  void _initializeParticles() {
    final random = math.Random();
    for (int i = 0; i < _particleCount; i++) {
      _particles.add(Particle(
        x: random.nextDouble(),
        y: random.nextDouble(),
        size: 2 + random.nextDouble() * 8,
        speed: 0.1 + random.nextDouble() * 0.3,
        opacity: 0.1 + random.nextDouble() * 0.3,
        direction: random.nextDouble() * 2 * math.pi,
      ));
    }
  }

  @override
  Widget build(BuildContext context) {
    final isDark = Theme.of(context).brightness == Brightness.dark;
    final defaultColors = widget.colors ?? (
      isDark ? [
        const Color(0xFF1a1a2e),
        const Color(0xFF16213e),
        const Color(0xFF0f3460),
        const Color(0xFF533483),
      ] : [
        const Color(0xFFf8f9fa),
        const Color(0xFFe9ecef),
        const Color(0xFFdee2e6),
        const Color(0xFFadb5bd),
      ]
    );

    return Stack(
      children: [
        // Animated Gradient Background
        AnimatedBuilder(
          animation: _gradientAnimation,
          builder: (context, child) {
            return Container(
              decoration: BoxDecoration(
                gradient: _buildAnimatedGradient(defaultColors),
              ),
            );
          },
        ),
        
        // Floating Particles
        if (widget.enableParticles)
          AnimatedBuilder(
            animation: _particleAnimation,
            builder: (context, child) {
              return CustomPaint(
                painter: ParticlePainter(
                  particles: _particles,
                  animationValue: _particleAnimation.value,
                  isDark: isDark,
                ),
                size: Size.infinite,
              );
            },
          ),
        
        // Liquid Glass Overlay
        _buildLiquidGlassOverlay(isDark),
        
        // Content
        widget.child,
      ],
    );
  }

  Gradient _buildAnimatedGradient(List<Color> colors) {
    final animationValue = _gradientAnimation.value;
    
    // Create shifting gradient based on animation
    final shiftedColors = <Color>[];
    for (int i = 0; i < colors.length; i++) {
      final colorIndex = (i + animationValue * colors.length) % colors.length;
      final baseIndex = colorIndex.floor();
      final nextIndex = (baseIndex + 1) % colors.length;
      final t = colorIndex - baseIndex;
      
      shiftedColors.add(Color.lerp(
        colors[baseIndex],
        colors[nextIndex],
        t,
      )!);
    }
    
    return RadialGradient(
      center: Alignment(
        math.sin(animationValue * 2 * math.pi) * 0.3,
        math.cos(animationValue * 2 * math.pi) * 0.3,
      ),
      radius: 1.5 + math.sin(animationValue * math.pi) * 0.5,
      colors: shiftedColors,
      stops: const [0.0, 0.3, 0.6, 1.0],
    );
  }

  Widget _buildLiquidGlassOverlay(bool isDark) {
    return Positioned.fill(
      child: CustomPaint(
        painter: LiquidGlassPainter(
          animationValue: _gradientAnimation.value,
          isDark: isDark,
        ),
      ),
    );
  }
}

class Particle {
  double x;
  double y;
  final double size;
  final double speed;
  final double opacity;
  final double direction;
  
  Particle({
    required this.x,
    required this.y,
    required this.size,
    required this.speed,
    required this.opacity,
    required this.direction,
  });
  
  void update() {
    x += math.cos(direction) * speed * 0.01;
    y += math.sin(direction) * speed * 0.01;
    
    // Wrap around screen
    if (x > 1.1) x = -0.1;
    if (x < -0.1) x = 1.1;
    if (y > 1.1) y = -0.1;
    if (y < -0.1) y = 1.1;
  }
}

class ParticlePainter extends CustomPainter {
  final List<Particle> particles;
  final double animationValue;
  final bool isDark;
  
  ParticlePainter({
    required this.particles,
    required this.animationValue,
    required this.isDark,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..style = PaintingStyle.fill;
    
    for (final particle in particles) {
      particle.update();
      
      final x = particle.x * size.width;
      final y = particle.y * size.height;
      
      // Create glowing effect
      final glowPaint = Paint()
        ..color = (isDark ? Colors.white : Colors.black).withOpacity(
          particle.opacity * 0.3 * (0.5 + 0.5 * math.sin(animationValue * 2 * math.pi)),
        )
        ..maskFilter = MaskFilter.blur(BlurStyle.normal, particle.size * 2);
      
      canvas.drawCircle(
        Offset(x, y),
        particle.size * 2,
        glowPaint,
      );
      
      // Draw particle
      paint.color = (isDark ? Colors.white : Colors.black).withOpacity(
        particle.opacity * (0.7 + 0.3 * math.sin(animationValue * 2 * math.pi + particle.x * 10)),
      );
      
      canvas.drawCircle(
        Offset(x, y),
        particle.size,
        paint,
      );
    }
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

class LiquidGlassPainter extends CustomPainter {
  final double animationValue;
  final bool isDark;
  
  LiquidGlassPainter({
    required this.animationValue,
    required this.isDark,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()
      ..style = PaintingStyle.fill;
    
    // Create liquid glass effect with multiple layers
    _drawLiquidLayer(canvas, size, paint, 0, 0.05);
    _drawLiquidLayer(canvas, size, paint, 0.3, 0.03);
    _drawLiquidLayer(canvas, size, paint, 0.6, 0.02);
  }
  
  void _drawLiquidLayer(Canvas canvas, Size size, Paint paint, double offset, double opacity) {
    final path = Path();
    final waveHeight = size.height * 0.1;
    final waveLength = size.width * 0.3;
    
    path.moveTo(0, size.height);
    
    for (double x = 0; x <= size.width; x += 5) {
      final y = size.height * 0.8 + 
          math.sin((x / waveLength + animationValue * 2 + offset) * 2 * math.pi) * waveHeight * 0.5 +
          math.sin((x / (waveLength * 0.7) + animationValue * 1.5 + offset) * 2 * math.pi) * waveHeight * 0.3;
      
      path.lineTo(x, y);
    }
    
    path.lineTo(size.width, size.height);
    path.close();
    
    paint.color = (isDark ? Colors.white : Colors.black).withOpacity(opacity);
    canvas.drawPath(path, paint);
    
    // Add shimmer effect
    final shimmerPaint = Paint()
      ..shader = LinearGradient(
        begin: Alignment.topLeft,
        end: Alignment.bottomRight,
        colors: [
          Colors.transparent,
          (isDark ? Colors.white : Colors.black).withOpacity(opacity * 0.5),
          Colors.transparent,
        ],
        stops: [
          0.0,
          (animationValue + offset) % 1.0,
          1.0,
        ],
      ).createShader(Rect.fromLTWH(0, 0, size.width, size.height));
    
    canvas.drawPath(path, shimmerPaint);
  }

  @override
  bool shouldRepaint(covariant CustomPainter oldDelegate) => true;
}

// Preset background configurations
class BackgroundPresets {
  static const List<Color> oceanBreeze = [
    Color(0xFF667eea),
    Color(0xFF764ba2),
    Color(0xFF6B73FF),
    Color(0xFF000DFF),
  ];
  
  static const List<Color> sunsetGlow = [
    Color(0xFFff9a9e),
    Color(0xFFfecfef),
    Color(0xFFfecfef),
    Color(0xFFff9a9e),
  ];
  
  static const List<Color> forestMist = [
    Color(0xFF134e5e),
    Color(0xFF71b280),
    Color(0xFF134e5e),
    Color(0xFF71b280),
  ];
  
  static const List<Color> cosmicDust = [
    Color(0xFF2c3e50),
    Color(0xFF3498db),
    Color(0xFF2c3e50),
    Color(0xFF3498db),
  ];
}
# LunVex Code - Thinking Animations

## Overview

LunVex Code features customizable thinking animations that display while the AI is processing. We've replaced the original whale animation with more thematic options suitable for an AI coding assistant.

## Available Animations

### 1. **No Animation** (Default)
Simple "Thinking..." text without animation.

### 2. **Pulsing Orb**
A futuristic AI core with pulsing energy rings.

**Features:**
- Robot with animated eyes and mouth
- Terminal showing real code snippets
- Changing status messages (Thinking, Processing, Analyzing, Coding)
- Animated terminal borders

**Preview:**
```
╔══════════════════════════════╗
║    print('Hello, World!')   ║
╔══════════════════════════════╗

    ╔══════════════╗    
    ║ █ █ █ █ █ █ █ ║    
    ╚══════════════╝    
       /        \       
      /  O    O  \      
     /            \     
    /    ────    \    
   /              \   

  Thinking...
```

### 3. **Neural Network**
An animated neural network with data flow visualization.

**Features:**
- Pulsing neural network nodes
- Binary data flow patterns
- Professional AI-themed design
- Status messages (Analyzing, Processing, Learning, Optimizing)

**Preview:**
```
╔══════════════════════════════════════╗
║ Neural Network Processing ║
╚══════════════════════════════════════╝

              [01010101]

               ●───○───○    
              / \ / \ / \   
             ○───●───○───○  
              \ / \ / \ /   
               ○───○───●    

  Processing...
```

### 4. **Coding Robot**
A robot typing with a terminal showing code snippets.

**Features:**
- Pulsing central orb
- Rotating inner and outer rings
- Futuristic design
- Status messages (Thinking, Processing, Computing, Generating)

**Preview:**
```
╔══════════════════════════════════════╗
║ AI Processing Core ║
╚══════════════════════════════════════╝

              ○ ○ ○ ○ 

                        
                  (●)   
                        

              ◉ ◉ ◉ ◉ 

  Computing...
```

## Configuration

### Environment Variable
Set the `LUNVEX_ANIMATION` environment variable to choose your animation:

```bash
# Bash/Zsh
export LUNVEX_ANIMATION="neural"

# Fish
set -x LUNVEX_ANIMATION "orb"

# One-time use
LUNVEX_ANIMATION="robot" python -m lunvex_code.cli
```

**Available values:**
- `none` - No animation (default)
- `orb` - Pulsing orb
- `robot` - Coding robot
- `neural` - Neural network

### Programmatic Usage
You can also specify the animation type when calling `print_thinking()`:

```python
from lunvex_code.ui import print_thinking

with print_thinking(animation_type="neural"):
    # AI thinking/processing code here
    pass
```

## Demo Script

Run the demo to see all animations:

```bash
python demo_animations.py
```

## Technical Details

### Animation Classes
- `None` - No animation (default)
- `PulsingOrb` - Pulsing core animation
- `CodingRobot` - Robot with terminal animation
- `NeuralNetwork` - Neural network animation

### Frame Rate
All animations run at 8 FPS for smooth display.

### Customization
Each animation class can be extended or modified:
- Change colors by modifying the Rich markup
- Add new frames to the animation sequences
- Customize text messages and status updates

## Adding New Animations

To add a new animation:

1. Create a new class inheriting from the animation pattern
2. Implement `get_frame()`, `update()`, and `__rich__()` methods
3. Add to `get_animation()` function
4. Update documentation

Example skeleton:
```python
class NewAnimation:
    def __init__(self, width: int = 40):
        self.width = width
        self.frame = 0
    
    def get_frame(self) -> Text:
        # Return Rich Text for current frame
        pass
    
    def update(self) -> None:
        # Update animation state
        self.frame += 1
    
    def __rich__(self) -> Text:
        self.update()
        return Text.from_markup(self.get_frame())
```

## Why We Changed from the Whale

The original whale animation was cute but didn't align with the AI coding assistant theme. Our new animations:

1. **Thematically appropriate** - Better represents AI/tech
2. **More professional** - Suitable for development environments
3. **Customizable** - Users can choose their preferred style
4. **Extensible** - Easy to add new animations
5. **Performance optimized** - Smooth 8 FPS animation

## Troubleshooting

### Animation Not Showing
- Ensure Rich library is installed: `pip install rich`
- Check terminal supports ANSI colors
- Try reducing terminal width if animation is cut off

### Colors Not Displaying
- Set `FORCE_COLOR=1` environment variable
- Check terminal color support with `python -c "from rich import print; print('[red]test[/red]')"`

### Performance Issues
- Reduce refresh rate by modifying `refresh_per_second` in `print_thinking()`
- Disable animation with minimal interface mode

## Future Enhancements

Planned features:
- [ ] User preferences file (`.lunvexrc`)
- [ ] Animation speed control
- [ ] Custom animation themes
- [ ] Seasonal/holiday animations
- [ ] Integration with system theme (light/dark mode)

---

*Enjoy your new thinking animations! The AI coding experience just got more engaging.*
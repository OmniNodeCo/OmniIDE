/**
 * Badge Generator (used for local test only)
 * @author OmniNodeCo
 */

const COLOR_MAP = {
  blue:        '2580f7',
  green:       '3fb950',
  red:         'f85149',
  yellow:      'd29922',
  orange:      'db6d28',
  purple:      'a371f7',
  pink:        'f778ba',
  gray:        '6e7681',
  grey:        '6e7681',
  brightgreen: '44cc11',
  cyan:        '00bcd4',
  black:       '24292f',
  white:       'f6f8fa',
};

function parseColor(color = 'blue') {
  return COLOR_MAP[color.toLowerCase()] || color.replace('#', '');
}

module.exports = { parseColor };
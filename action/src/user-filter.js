/**
 * User Filter
 * @author OmniNodeCo
 */

/**
 * @param {Object|null} config   - Parsed .viewsbadge config
 * @param {string}      visitor  - GitHub username of visitor
 * @returns {boolean}
 */
function isExcluded(config, visitor) {
  if (!config)  return false;
  if (!visitor) return false;

  const list = config.exclude || [];

  if (!Array.isArray(list)) return false;

  return list.some(
    entry => typeof entry === 'string' &&
    entry.toLowerCase() === visitor.toLowerCase()
  );
}

module.exports = { isExcluded };
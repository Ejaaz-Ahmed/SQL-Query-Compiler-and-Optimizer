/**
 * Icon component — Bootstrap Icons wrapper for consistent sizing and alignment.
 */
import React from 'react';

const Icon = ({ name, className = '', size, style = {}, ...props }) => (
  <i
    className={`bi bi-${name} app-icon ${className}`.trim()}
    style={size ? { fontSize: size, ...style } : style}
    aria-hidden="true"
    {...props}
  />
);

export const SectionTitle = ({ icon, children, chevron = null, className = '' }) => (
  <span className={`section-title ${className}`.trim()}>
    {icon && <Icon name={icon} className="section-title-icon" />}
    <span>{children}</span>
    {chevron && <Icon name={chevron} className="section-title-chevron" size="0.85rem" />}
  </span>
);

export default Icon;

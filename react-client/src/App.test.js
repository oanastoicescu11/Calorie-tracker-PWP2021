import { render, screen } from '@testing-library/react';
import PWPApp from './PWPApp';

test('renders learn react link', () => {
  render(<PWPApp />);
  const linkElement = screen.getByText(/learn react/i);
  expect(linkElement).toBeInTheDocument();
});

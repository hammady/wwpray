/* eslint-disable @typescript-eslint/no-var-requires */
/** @type {import('tailwindcss').Config} */
export default {
	content: ['./src/**/*.{html,js,svelte,ts}'],
	theme: {
		extend: {
			spacing: {
				navbar: '6rem'
			},
			colors: {
				danger: 'hsl(var(--danger) / <alpha-value>)',
				bg01: 'hsl(var(--bg01) / <alpha-value>)'
			},
			boxShadow: {
				card: '0px 4px 4px 0px rgba(0, 0, 0, 0.05)'
			}
		}
	},
	plugins: [require('@tailwindcss/typography'), require('daisyui')],
	daisyui: {
		themes: [
			{
				light: {
					...require('daisyui/src/theming/themes')['[data-theme=light]'],
					'--danger': '8 80% 56%',
					'--bg01': '210 20% 98%'
				}
			}
		]
	}
};

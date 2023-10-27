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
				danger: 'hsl(var(--danger) / <alpha-value>)'
			}
		}
	},
	plugins: [require('@tailwindcss/typography'), require('daisyui')],
	daisyui: {
		themes: [
			{
				light: {
					...require('daisyui/src/theming/themes')['[data-theme=light]'],
					'--danger': '8 80% 56%'
				}
			}
		]
	}
};

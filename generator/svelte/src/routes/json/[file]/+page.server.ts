import type { PageServerLoad } from './$types';

export const load = (async ({params: {file}}) => {
    const data = (await import(`../../${file}.json`));

    return data.default
}) satisfies PageServerLoad;
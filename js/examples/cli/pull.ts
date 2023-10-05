const fs = require('fs');
const path = require('path');
const{ execSync } = require('child_process');

const pull = ({name, url}: {name: string, url: string}, outdir: string) => {
    const out = `./${outdir}/${name}`;

    const cmd = fs.existsSync(out) ? `cd ${out} && git pull` : `git clone ${url} ${out}`

    console.log(`Fetching ${name} from ${url}`);

    execSync(cmd, {
        stdio: [0, 1, 2], // we need this so node will print the command output
        cwd: path.resolve(__dirname, ''), // path to where you want to save the file
    })
}

const deps: Array<{name: string, url: string}> = [
    {name: 'gsl', url: 'https://github.com/microsoft/GSL.git' },
    {name: 'etl', url: 'https://github.com/ETLCPP/etl.git' },
    {name: 'fmt', url: 'https://github.com/fmtlib/fmt.git' },
    {name: 'sml', url: 'https://github.com/boost-ext/sml.git' },
];

deps.forEach((r) => pull(r, 'build'))

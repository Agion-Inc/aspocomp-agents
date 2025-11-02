import Replicate from 'replicate';
import { config } from 'dotenv';
import yargs from 'yargs';
import { hideBin } from 'yargs/helpers';
import ora from 'ora';
import chalk from 'chalk';
import * as path from 'path';
import * as fs from 'fs';
import { downloadFile } from './utils/download';

// Load environment variables
config({
  path: process.env.NODE_ENV === 'development' ? '.env.local' : '.env'
});

interface SeedanceOptions {
  prompt: string;
  output?: string;
  folder?: string;
}

async function generateSeedanceVideo(options: SeedanceOptions) {
  const spinner = ora('Initializing Seedance video generation...').start();

  try {
    if (!process.env.REPLICATE_API_TOKEN) {
      throw new Error('REPLICATE_API_TOKEN is required in .env file');
    }

    const replicate = new Replicate({
      auth: process.env.REPLICATE_API_TOKEN,
    });

    const input = {
      prompt: options.prompt,
    };

    spinner.text = 'Generating video with Seedance 1 Pro Fast...';
    const output = await replicate.run("bytedance/seedance-1-pro-fast", { input });

    // Handle output - Replicate returns different formats
    let videoUrl: string | undefined;
    
    if (typeof output === 'string') {
      videoUrl = output;
    } else if (Array.isArray(output)) {
      videoUrl = output.find(u => typeof u === 'string');
    } else if (output && typeof output === 'object') {
      // Try common fields
      const maybeOutput = (output as any).output;
      if (typeof maybeOutput === 'string') {
        videoUrl = maybeOutput;
      } else if (Array.isArray(maybeOutput)) {
        videoUrl = maybeOutput.find((u: unknown) => typeof u === 'string');
      } else if (Array.isArray((output as any).urls)) {
        videoUrl = (output as any).urls.find((u: unknown) => typeof u === 'string');
      } else if (typeof (output as any).url === 'string') {
        videoUrl = (output as any).url;
      }
    }

    // If output has a url() method (as shown in the example)
    if (!videoUrl && output && typeof (output as any).url === 'function') {
      videoUrl = (output as any).url();
    }

    if (!videoUrl) {
      console.error('Raw output:', JSON.stringify(output, null, 2));
      throw new Error('Failed to generate video: Invalid output from API');
    }

    // Handle output file
    const outputFolder = options.folder || 'public/videos';
    if (!fs.existsSync(outputFolder)) {
      fs.mkdirSync(outputFolder, { recursive: true });
    }

    const filename = options.output || `seedance-${Date.now()}.mp4`;
    const outputPath = path.join(outputFolder, filename);

    spinner.text = 'Downloading video...';
    await downloadFile(videoUrl, outputPath);

    spinner.succeed(chalk.green(`Video generated successfully: ${outputPath}`));
    console.log(chalk.dim(`Video URL: ${videoUrl}`));
    return outputPath;
  } catch (error: unknown) {
    spinner.fail(chalk.red(`Error generating video: ${error instanceof Error ? error.message : 'Unknown error'}`));
    throw error;
  }
}

async function main() {
  const argv = await yargs(hideBin(process.argv))
    .option('prompt', {
      alias: 'p',
      type: 'string',
      description: 'Text description of the desired video',
      demandOption: true
    })
    .option('output', {
      alias: 'o',
      type: 'string',
      description: 'Output filename'
    })
    .option('folder', {
      alias: 'f',
      type: 'string',
      description: 'Output folder path',
      default: 'public/videos'
    })
    .help()
    .argv;

  try {
    await generateSeedanceVideo({
      prompt: argv.prompt,
      output: argv.output,
      folder: argv.folder
    });
  } catch (error) {
    process.exit(1);
  }
}

// Run if this is the main module
main().catch(error => {
  console.error(error);
  process.exit(1);
});

export { generateSeedanceVideo };


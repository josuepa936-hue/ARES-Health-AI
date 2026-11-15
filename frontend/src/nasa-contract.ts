/** Official NASA OSDR research manifests are not astronaut telemetry. */
import { z } from 'zod';
const nasaFile = z.object({
  file_name: z.string(),
  category: z.string(),
  size_bytes: z.number().int().nonnegative(),
  file_url: z.string().url().refine((url) => url.startsWith('https://osdr.nasa.gov/')),
});
export const nasaStudySchema = z.object({
  schema_version: z.literal('1.2-osdr'),
  accession: z.literal('OSD-87'),
  study_title: z.string(),
  source_organization: z.literal('NASA Open Science Data Repository'),
  study_url: z.literal('https://osdr.nasa.gov/bio/repo/data/studies/OSD-87'),
  api_url: z.literal('https://osdr.nasa.gov/osdr/data/osd/files/87'),
  organism: z.string(),
  tissue: z.string(),
  mission_context: z.literal('STS-135'),
  data_provenance: z.literal('public_space_biology_research'),
  file_catalog_count: z.number().int().nonnegative(),
  visible_public_files: z.number().int().nonnegative(),
  file_categories: z.array(z.object({
    category: z.string(),
    count: z.number().int().nonnegative(),
  })).max(25),
  files: z.array(nasaFile).max(25),
  sample_preview_available: z.boolean(),
  disclaimer: z.string(),
});
export type NasaStudy = z.infer<typeof nasaStudySchema>;
export const nasaSamplesSchema = z.object({
  schema_version: z.literal('1.2-osdr-samples'),
  accession: z.literal('OSD-87'),
  file_name: z.literal('GLDS-87_array_SampleTable_GLmicroarray.csv'),
  data_provenance: z.literal('public_space_biology_research'),
  sample_count: z.number().int().min(1).max(64),
  column_names: z.array(z.string()).min(1).max(20),
  rows: z.array(z.record(z.string())).min(1).max(64),
  reference_url: z.literal('https://osdr.nasa.gov/bio/repo/data/studies/OSD-87'),
  disclaimer: z.string(),
}).refine((data) => data.sample_count === data.rows.length);
export type NasaSamples = z.infer<typeof nasaSamplesSchema>;

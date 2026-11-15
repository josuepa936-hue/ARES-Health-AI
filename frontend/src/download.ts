import type { ReviewReport } from './contracts';
import type { ComprehensiveReport } from './copilot-contract';

/** Export an existing validated report without changing its schema or review status. */
export function downloadReport(report: ReviewReport | ComprehensiveReport) {
  const url = URL.createObjectURL(
    new Blob([JSON.stringify(report, null, 2)], { type: 'application/json' }),
  );
  const anchor = document.createElement('a');
  anchor.href = url;
  anchor.download = 'ares-synthetic-review.json';
  document.body.append(anchor);
  anchor.click();
  anchor.remove();
  setTimeout(() => URL.revokeObjectURL(url), 0);
}

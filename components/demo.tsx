"use client";

import * as React from "react";
import { IconArrowRight, IconDownload, IconMail, IconTrash } from "@tabler/icons-react";
import { Button } from "@/components/ui/button";

const settings = {
  label: "Get started",
  loading: false,
  disabled: false,
};

export default function Demo(props: Partial<typeof settings>) {
  const s = { ...settings, ...props };

  return (
    <div className="flex min-h-[360px] w-full flex-col items-center justify-center gap-6 px-6 py-10">
      <div className="flex flex-wrap items-center justify-center gap-3">
        <Button
          loading={s.loading}
          disabled={s.disabled}
          rightIcon={<IconArrowRight stroke={1.75} />}
          rightIconMotion="arrow"
        >
          {s.label}
        </Button>
        <Button variant="secondary" disabled={s.disabled}>
          Secondary
        </Button>
        <Button variant="outline" disabled={s.disabled}>
          Outline
        </Button>
        <Button variant="ghost" disabled={s.disabled}>
          Ghost
        </Button>
      </div>
      <div className="flex flex-wrap items-center justify-center gap-3">
        <Button
          variant="destructive"
          disabled={s.disabled}
          leftIcon={<IconTrash stroke={1.75} />}
          leftIconMotion="trash"
        >
          Delete
        </Button>
        <Button
          variant="outline"
          size="sm"
          disabled={s.disabled}
          leftIcon={<IconMail stroke={1.75} />}
          leftIconMotion="mail"
        >
          Invite
        </Button>
        <Button
          variant="secondary"
          size="lg"
          disabled={s.disabled}
          rightIcon={<IconDownload stroke={1.75} />}
          rightIconMotion="download"
        >
          Download
        </Button>
        <Button variant="outline" size="icon" aria-label="Send" disabled={s.disabled}>
          <IconArrowRight stroke={1.75} />
        </Button>
        <Button variant="link" disabled={s.disabled}>
          Read the docs
        </Button>
      </div>
    </div>
  );
}

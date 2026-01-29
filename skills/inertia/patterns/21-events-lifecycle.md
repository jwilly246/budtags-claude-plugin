# Pattern 21: Events & Lifecycle

## Overview

Inertia provides event hooks at global and per-request levels for monitoring and controlling the navigation lifecycle.

---

## Global Event Listeners

### Register Listeners

```tsx
import { router } from '@inertiajs/react';

// In app.tsx or layout component
useEffect(() => {
  const removeStart = router.on('start', (event) => {
    console.log('Starting visit to:', event.detail.visit.url);
  });

  const removeFinish = router.on('finish', () => {
    console.log('Visit finished');
  });

  // Cleanup on unmount
  return () => {
    removeStart();
    removeFinish();
  };
}, []);
```

---

## Event Types

### before

Fires before making the request. Return `false` to cancel:

```tsx
router.on('before', (event) => {
  if (!confirm('Leave this page?')) {
    event.preventDefault();
  }
});
```

### start

Fires when the request starts:

```tsx
router.on('start', (event) => {
  const { url, method } = event.detail.visit;
  console.log(`${method.toUpperCase()} ${url}`);
});
```

### progress

Fires during file uploads:

```tsx
router.on('progress', (event) => {
  const { percentage } = event.detail.progress;
  setUploadProgress(percentage);
});
```

### success

Fires on successful response:

```tsx
router.on('success', (event) => {
  const { component, props } = event.detail.page;
  console.log('Loaded:', component);
});
```

### error

Fires on validation errors (422):

```tsx
router.on('error', (event) => {
  console.error('Validation errors:', event.detail.errors);
});
```

### finish

Fires after success or error:

```tsx
router.on('finish', () => {
  setLoading(false);
});
```

### navigate

Fires after page component is swapped:

```tsx
router.on('navigate', (event) => {
  // Good for analytics
  analytics.track('pageview', {
    url: event.detail.page.url,
    title: document.title,
  });
});
```

### invalid

Fires on invalid responses (non-Inertia):

```tsx
router.on('invalid', (event) => {
  const { status } = event.detail.response;

  if (status === 419) {
    toast.error('Session expired');
    window.location.reload();
  }
});
```

### exception

Fires on unexpected errors:

```tsx
router.on('exception', (event) => {
  console.error('Unexpected error:', event.detail.exception);
  toast.error('Something went wrong');
});
```

---

## Per-Request Callbacks

### With router.visit()

```tsx
router.visit('/users', {
  onBefore: (visit) => {
    return confirm('Continue?');
  },
  onStart: () => {
    setLoading(true);
  },
  onProgress: (progress) => {
    setProgress(progress.percentage);
  },
  onSuccess: (page) => {
    toast.success('Loaded!');
  },
  onError: (errors) => {
    toast.error(Object.values(errors)[0]);
  },
  onFinish: () => {
    setLoading(false);
  },
  onCancel: () => {
    console.log('Request cancelled');
  },
});
```

### With useForm

```tsx
const { post } = useForm({ name: '' });

post('/users', {
  onBefore: () => confirm('Submit?'),
  onSuccess: () => {
    reset();
    closeModal();
  },
  onError: (errors) => {
    toast.error(errors.name || 'Validation failed');
  },
  onFinish: () => {
    setSubmitting(false);
  },
});
```

### With Link

```tsx
<Link
  href="/logout"
  method="post"
  onBefore={() => confirm('Logout?')}
  onSuccess={() => toast.success('Logged out')}
>
  Logout
</Link>
```

---

## Event Object Structure

```tsx
router.on('start', (event) => {
  // event.detail.visit contains:
  const {
    url,        // Target URL
    method,     // HTTP method
    data,       // Request data
    replace,    // Replace history?
    preserveScroll,
    preserveState,
    only,       // Partial reload props
    except,     // Excluded props
    headers,    // Custom headers
  } = event.detail.visit;
});

router.on('success', (event) => {
  // event.detail.page contains:
  const {
    component,  // Page component name
    props,      // Page props
    url,        // Final URL
    version,    // Asset version
  } = event.detail.page;
});
```

---

## Common Use Cases

### Analytics

```tsx
router.on('navigate', (event) => {
  // Google Analytics
  gtag('config', 'GA_TRACKING_ID', {
    page_path: event.detail.page.url,
  });

  // Or any analytics service
  analytics.page(event.detail.page.url);
});
```

### Loading Indicator

```tsx
function useGlobalLoading() {
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const start = router.on('start', () => setLoading(true));
    const finish = router.on('finish', () => setLoading(false));
    return () => { start(); finish(); };
  }, []);

  return loading;
}
```

### Unsaved Changes Warning

```tsx
function useUnsavedChangesWarning(isDirty: boolean) {
  useEffect(() => {
    if (!isDirty) return;

    const handler = router.on('before', (event) => {
      if (!confirm('You have unsaved changes. Leave anyway?')) {
        event.preventDefault();
      }
    });

    return handler;
  }, [isDirty]);
}

// Usage
const { isDirty } = useForm({ name: '' });
useUnsavedChangesWarning(isDirty);
```

### Session Timeout Handling

```tsx
useEffect(() => {
  return router.on('invalid', (event) => {
    if (event.detail.response.status === 419) {
      toast.error('Session expired. Please log in again.');
      setTimeout(() => {
        window.location.href = '/login';
      }, 2000);
    }
  });
}, []);
```

---

## BudTags Example

```tsx
// In MainLayout.tsx
export default function MainLayout({ children }) {
  const [navigating, setNavigating] = useState(false);

  useEffect(() => {
    const start = router.on('start', () => setNavigating(true));
    const finish = router.on('finish', () => setNavigating(false));

    const invalid = router.on('invalid', (event) => {
      if (event.detail.response.status === 419) {
        toast.error('Session expired');
      }
    });

    return () => {
      start();
      finish();
      invalid();
    };
  }, []);

  return (
    <div>
      {navigating && <TopLoadingBar />}
      <Navbar />
      <main>{children}</main>
    </div>
  );
}
```

---

## Next Steps

- **SSR** → Read `22-ssr.md`
- **Testing** → Read `23-testing.md`

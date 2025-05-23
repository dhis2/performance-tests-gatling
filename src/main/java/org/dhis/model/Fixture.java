package org.dhis.model;

import java.util.Map;

public class Fixture {
    private Map<String, Object> resource;
    private String onCreatePath;
    private String onConflictPath;

    public Map<String, Object> getResource() {
        return resource;
    }

    public void setResource(Map<String, Object> resource) {
        this.resource = resource;
    }

    public String getOnCreatePath() {
        return onCreatePath;
    }

    public void setOnCreatePath(String onCreatePath) {
        this.onCreatePath = onCreatePath;
    }

    public String getOnConflictPath() {
        return onConflictPath;
    }

    public void setOnConflictPath(String onConflictPath) {
        this.onConflictPath = onConflictPath;
    }
}
